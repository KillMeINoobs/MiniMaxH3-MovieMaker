from array import array
from copy import deepcopy
import wave

import pytest

from kmin_video_director.contracts import AudioTimeline, Project, RenderProfile, RenderResult, resolve_project
from kmin_video_director.errors import ContractError
from tests.contracts.example_data import profile
from tests.assembly.support import prepared_project, cpu_results
from tests.media.support import command, raw_video, numbered_frame


def test_generate_uses_explicit_useful_pcm_not_an_implicit_source_track(tmp_path):
    from kmin_video_director.media.normalize import pcm_manifest
    from kmin_video_director.media.backend import backend
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    p, ctx = prepared_project(tmp_path, frames=6)
    p, results = cpu_results(p, ctx)
    locator = {'scheme': 'project_relative', 'path': 'generated-impulse.wav'}
    samples = array('h', [0]) * 12000; samples[4000] = 21000
    with wave.open(str(tmp_path / locator['path']), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(48000); f.writeframes(samples.tobytes())
    _, _, versions = backend(ctx)
    pcm, count = pcm_manifest(locator, 48000, 1, versions, ctx)
    rd = results[0].to_dict(); rd['artifacts'].append(pcm.to_dict())
    pd = p.to_dict(); pd['results'][rd['id']] = rd; pd['media'][pcm.id] = pcm.to_dict()
    p = Project.from_dict(pd); result = RenderResult.from_dict(rd)
    ad = p['audio_timeline']; ad['mode'] = 'generate'
    out = assemble_export(p, (result,), AudioTimeline.from_dict(ad), DEFAULT_POLICY, context=ctx)
    raw = command([ctx.versions['ffmpeg_path'], '-v', 'error', '-i', str(tmp_path / out.result['artifacts'][0]['locator']['path']),
        '-map', '0:a:0', '-f', 's16le', 'pipe:1'])
    assert raw == samples.tobytes()
    assert out.report['audio']['final_encode_count'] == 1


def test_preserve_cannot_silently_replace_a_muted_missing_pcm(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    p, ctx = prepared_project(tmp_path, frames=6, sound=True)
    p, results = cpu_results(p, ctx)
    pd = p.to_dict(); pd['normalization']['report']['pcm_media'] = None
    p = Project.from_dict(pd)
    with pytest.raises(ValueError, match='AUDIO_SYNC_MISMATCH'):
        assemble_export(p, results, AudioTimeline.from_dict(p['audio_timeline']), DEFAULT_POLICY, context=ctx)


def split_scenes(project, ctx, ranges):
    from kmin_video_director.media.project import apply_plan
    from kmin_video_director.planning.windows import plan_windows
    data = project.to_dict()
    original = data['segments'][0]
    data.update(windows={}, results={}, active_result_by_window={}, spatial_transforms={})
    data['segments'] = []
    for i, (a, b, selected) in enumerate(ranges):
        scene = deepcopy(original)
        scene.update(id=f'audio-scene-{i}', selected=selected,
                     boundary_before='first' if i == 0 else 'cut', continuity_group_id=f'audio-shot-{i}')
        scene['useful_range'] = scene['source_range'] = {'start': a, 'end': b}
        data['segments'].append(scene)
    project = Project.from_dict(data)
    return apply_plan(project, plan_windows(resolve_project(project), RenderProfile.from_dict(profile()), context=ctx))


def supplied_pcm(project, results, ctx, segment_id, samples, rate):
    from kmin_video_director.media.backend import backend
    from kmin_video_director.media.normalize import pcm_manifest
    locator = {'scheme': 'project_relative', 'path': 'supplied-useful.wav'}
    with wave.open(str(ctx.asset_root / locator['path']), 'wb') as dst:
        dst.setnchannels(1); dst.setsampwidth(2); dst.setframerate(rate)
        dst.writeframes(samples.tobytes())
    _, _, versions = backend(ctx)
    pcm, _ = pcm_manifest(locator, rate, 1, versions, ctx)
    data = project.to_dict()
    updated = []
    for result in results:
        record = result.to_dict()
        if record['segment_id'] == segment_id:
            record['artifacts'].append(pcm.to_dict())
            data['results'][record['id']] = record
            data['media'][pcm.id] = pcm.to_dict()
        updated.append(RenderResult.from_dict(record))
    return Project.from_dict(data), tuple(updated)


def scene_audio(project, modes):
    audio = project['audio_timeline']
    audio['decisions'] = [{'segment_id': scene['id'], 'mode': mode}
                          for scene, mode in zip(project['segments'], modes)]
    return AudioTimeline.from_dict(audio)


@pytest.mark.parametrize('modes', [('preserve', 'mute'), ('mute', 'preserve')])
def test_no_selected_audio_preserve_and_mute_export_six_video_only_frames(tmp_path, modes):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    project, ctx = prepared_project(tmp_path, 6, width=32, height=24)
    project = split_scenes(project, ctx, [(0, 3, True), (3, 6, True)])
    project, results = cpu_results(project, ctx)
    assert project['normalization']['report']['pcm_media'] is None
    out = assemble_export(project, results, scene_audio(project, modes), DEFAULT_POLICY, context=ctx)
    media = out.result['artifacts'][0]
    assert media['probe']['audio'] is None
    assert out.report['audio']['stream'] is False
    assert out.result['coverage']['useful_frames'] == 6
    assert raw_video(tmp_path / media['locator']['path']) == b''.join(numbered_frame(1000+i, 32, 24) for i in range(6))


@pytest.mark.parametrize('modes', [('preserve', 'generate'), ('generate', 'preserve')])
def test_audio_less_preserve_is_exact_silence_with_supplied_generate(tmp_path, modes):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    rate = 32000
    project, ctx = prepared_project(tmp_path, 6, width=32, height=24, sample_rate=rate)
    project = split_scenes(project, ctx, [(0, 3, True), (3, 6, True)])
    project, results = cpu_results(project, ctx)
    supplied = array('h', (300 + i % 47 for i in range(4000)))
    chosen = project['segments'][modes.index('generate')]['id']
    project, results = supplied_pcm(project, results, ctx, chosen, supplied, rate)
    out = assemble_export(project, results, scene_audio(project, modes), DEFAULT_POLICY, context=ctx)
    output = tmp_path / out.result['artifacts'][0]['locator']['path']
    actual = command([ctx.versions['ffmpeg_path'], '-v', 'error', '-nostdin', '-i', str(output),
                      '-map', '0:a:0', '-f', 's16le', 'pipe:1'])
    pieces = {'preserve': bytes(4000*2), 'generate': supplied.tobytes()}
    assert actual == b''.join(pieces[mode] for mode in modes)
    assert out.report['audio']['decoded_samples'] == 8000
    assert out.report['audio']['final_encode_count'] == 1
    assert out.result['coverage']['useful_frames'] == 6


def test_known_selected_audio_missing_pcm_still_rejects_mixed_preserve_mute(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    project, ctx = prepared_project(tmp_path, 6, width=32, height=24, sound=True)
    project = split_scenes(project, ctx, [(0, 3, True), (3, 6, True)])
    project, results = cpu_results(project, ctx)
    data = project.to_dict()
    data['normalization']['report']['pcm_media'] = None
    project = Project.from_dict(data)
    with pytest.raises(ContractError) as raised:
        assemble_export(project, results, scene_audio(project, ('preserve', 'mute')), DEFAULT_POLICY, context=ctx)
    assert raised.value.code == 'AUDIO_SYNC_MISMATCH'


def test_audio_less_preserve_does_not_hide_missing_generated_useful_pcm(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    project, ctx = prepared_project(tmp_path, 6, width=32, height=24)
    project = split_scenes(project, ctx, [(0, 3, True), (3, 6, True)])
    project, results = cpu_results(project, ctx)
    with pytest.raises(ContractError) as raised:
        assemble_export(project, results, scene_audio(project, ('preserve', 'generate')), DEFAULT_POLICY, context=ctx)
    assert raised.value.code == 'AUDIO_SYNC_MISMATCH'
    assert 'useful-trimmed PCM artifact per result' in str(raised.value)


def test_discontinuous_preserve_generate_keeps_absolute_q_and_one_phase_fit(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    q = lambda frame: (frame * 32000 + 12)//24
    project, ctx = prepared_project(tmp_path, 8, width=32, height=24, sound=True,
        sample_rate=32000, impulses=[q(1), q(2)-2, q(4)])
    project = split_scenes(project, ctx, [(0, 1, False), (1, 2, True), (2, 4, False), (4, 6, True), (6, 8, False)])
    project, results = cpu_results(project, ctx)
    supplied = array('h', (100 + i % 97 for i in range(q(6)-q(4))))
    project, results = supplied_pcm(project, results, ctx, 'audio-scene-3', supplied, 32000)
    audio = project['audio_timeline']
    audio['decisions'] = [{'segment_id': 'audio-scene-3', 'mode': 'generate'}]
    out = assemble_export(project, results, AudioTimeline.from_dict(audio),
                          {**DEFAULT_POLICY, 'selection': 'selected'}, context=ctx)
    pcm = project['normalization']['report']['pcm_media']
    with wave.open(str(tmp_path / pcm['locator']['path']), 'rb') as src:
        global_samples = array('h', src.readframes(src.getnframes()))
    expected = global_samples[q(1):q(1)+q(1)] + supplied
    output = tmp_path / out.result['artifacts'][0]['locator']['path']
    actual = command([ctx.versions['ffmpeg_path'], '-v', 'error', '-nostdin', '-i', str(output),
                      '-map', '0:a:0', '-f', 's16le', 'pipe:1'])
    assert len(expected) == 4000 == q(3)
    assert actual == expected.tobytes()
    assert out.report['audio']['sample_phase_corrections'] == [
        {'useful_range': {'start': 1, 'end': 2}, 'sample_phase_fit': -1}]
    assert out.report['audio']['final_encode_count'] == 1
