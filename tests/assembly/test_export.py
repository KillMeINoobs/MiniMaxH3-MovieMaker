from array import array

import pytest

from kmin_video_director.contracts import AudioTimeline, Project, RenderResult
from tests.assembly.support import prepared_project, cpu_results
from tests.media.support import raw_video, numbered_frame, command, multistream_video


@pytest.mark.parametrize('frames', [1, 24, 360])
def test_full_export_is_exact_and_uses_selected_cpu_outputs(tmp_path, frames):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    p, ctx = prepared_project(tmp_path, frames)
    p, results = cpu_results(p, ctx)
    out = assemble_export(p, results, AudioTimeline.from_dict(p['audio_timeline']), DEFAULT_POLICY, context=ctx)
    artifact = out.result['artifacts'][0]
    assert raw_video(tmp_path / artifact['locator']['path']) == b''.join(numbered_frame(i+1000) for i in range(frames))
    assert out.result['coverage']['useful_frames'] == frames
    assert out.report['video']['decoded_frames'] == frames
    assert out.report['audio']['stream'] is False
    assert out.result['validation']['gpu'] == 'not_performed'


@pytest.mark.parametrize('leading_audio', [False, True])
def test_export_uses_selected_absolute_video_stream_and_distinct_artifact_identity(tmp_path, leading_audio):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.backend import with_role
    from kmin_video_director.contracts.worker import ProjectLocator, StreamSelection
    frames = 6
    project, ctx = prepared_project(tmp_path, frames)
    project, results = cpu_results(project, ctx)
    artifact = multistream_video(tmp_path, count=frames, leading_audio=leading_audio)
    output_paths = []
    for slot in (0, 1):
        stream = slot + int(leading_audio)
        expected = b''.join(numbered_frame((slot + 1) * 1000 + i) for i in range(frames))
        assert raw_video(artifact, stream=stream) == expected
        chosen = probe_media(ProjectLocator(artifact.name), StreamSelection(video=stream), context=ctx).media
        assert chosen['fingerprint']['video_stream'] == stream
        assert chosen['probe']['audio'] is None
        result = results[0].to_dict()
        result['artifacts'] = [with_role(chosen, 'render_video').to_dict()]
        result['coverage']['pts_digest'] = chosen['probe']['video']['pts_digest']
        data = project.to_dict()
        data['results'][result['id']] = result
        selected_project = Project.from_dict(data)
        out = assemble_export(selected_project, (RenderResult.from_dict(result),),
            AudioTimeline.from_dict(project['audio_timeline']), DEFAULT_POLICY, context=ctx)
        path = tmp_path / out.result['artifacts'][0]['locator']['path']
        assert raw_video(path) == expected
        assert out.report['video']['decoded_frames'] == frames
        assert out.report['audio']['stream'] is False
        output_paths.append(path)
    assert output_paths[0] != output_paths[1]
    # A second selection must not overwrite the first selection's durable output.
    assert raw_video(output_paths[0]) == b''.join(numbered_frame(1000 + i) for i in range(frames))


def test_32000_global_boundary_impulses_and_one_final_pcm_encode(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    from kmin_video_director.media.timing import sample_boundary
    impulses = [sample_boundary(f, 32000) for f in (0, 1, 179, 180, 359)] + [480000 - 1]
    p, ctx = prepared_project(tmp_path, 360, sound=True, sample_rate=32000, impulses=impulses)
    p, results = cpu_results(p, ctx)
    out = assemble_export(p, results, AudioTimeline.from_dict(p['audio_timeline']), DEFAULT_POLICY, context=ctx)
    path = tmp_path / out.result['artifacts'][0]['locator']['path']
    raw = command([ctx.versions['ffmpeg_path'], '-v', 'error', '-i', str(path), '-map', '0:a:0', '-f', 's16le', 'pipe:1'])
    samples = array('h', raw)
    assert len(samples) == 480000
    assert [i for i, value in enumerate(samples) if value] == impulses
    assert out.report['audio']['global_pcm_samples'] == 480000
    assert out.report['audio']['final_encode_count'] == 1


def test_missing_unselected_changed_or_stale_results_never_fall_back(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    p, ctx = prepared_project(tmp_path)
    p, results = cpu_results(p, ctx)
    audio = AudioTimeline.from_dict(p['audio_timeline'])
    with pytest.raises(ValueError, match='PARTIAL_RESULT'):
        assemble_export(p, (), audio, DEFAULT_POLICY, context=ctx)
    extra = results[0].to_dict(); extra['id'] = 'unchosen'
    with pytest.raises(ValueError, match='STALE_DEPENDENCY'):
        assemble_export(p, (RenderResult.from_dict(extra),), audio, DEFAULT_POLICY, context=ctx)
    file = tmp_path / results[0]['artifacts'][0]['locator']['path']
    file.write_bytes(file.read_bytes() + b'changed')
    with pytest.raises(ValueError, match='SOURCE_CHANGED'):
        assemble_export(p, results, audio, DEFAULT_POLICY, context=ctx)


def test_mute_and_explicit_odd_codec_padding(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    p, ctx = prepared_project(tmp_path, sound=True)
    p, results = cpu_results(p, ctx)
    ad = p['audio_timeline']; ad['mode'] = 'mute'
    audio = AudioTimeline.from_dict(ad)
    with pytest.raises(ValueError, match='UNSUPPORTED_EXPORT_DIMENSIONS'):
        assemble_export(p, results, audio, {**DEFAULT_POLICY, 'codec': 'h264-aac'}, context=ctx)
    out = assemble_export(p, results, audio, {**DEFAULT_POLICY, 'codec': 'h264-aac', 'odd_dimensions': 'pad_even'}, context=ctx)
    assert out.report['export_dimensions'] == [38, 20]
    assert out.report['source_display_dimensions'] == [37, 19]
    assert out.report['audio']['stream'] is False


def test_aac_priming_and_no_accumulating_impulse_shift(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    impulses = [0, 2000, 100000, 198000]
    p, ctx = prepared_project(tmp_path, 100, width=38, height=20, sound=True, impulses=impulses)
    p, results = cpu_results(p, ctx)
    out = assemble_export(p, results, AudioTimeline.from_dict(p['audio_timeline']),
                          {**DEFAULT_POLICY, 'codec': 'h264-aac'}, context=ctx)
    path = tmp_path / out.result['artifacts'][0]['locator']['path']
    decoded = array('h', command([ctx.versions['ffmpeg_path'], '-v', 'error', '-i', str(path), '-map', '0:a:0', '-f', 's16le', 'pipe:1']))
    for expected in impulses:
        left, right = max(0, expected-8), min(len(decoded), expected+9)
        peak = max(range(left, right), key=lambda i: abs(decoded[i]))
        assert abs(peak-expected) <= 1
    assert out.report['audio']['codec_skip_samples'] == 1024, command([ctx.versions['ffprobe_path'], '-v', 'error',
        '-select_streams', '1', '-show_packets', '-show_entries', 'packet=pts,duration:packet_side_data=skip_samples,discard_padding',
        '-of', 'compact=p=0', str(path)]).decode()[:700]
    assert abs(out.report['audio']['decoded_samples'] - 200000) <= 2000


def test_selected_only_keeps_absolute_pcm_slices_through_technical_windows(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    from kmin_video_director.planning.windows import plan_windows
    from kmin_video_director.media.project import apply_plan
    from kmin_video_director.contracts import resolve_project, RenderProfile
    from tests.contracts.example_data import profile
    from kmin_video_director.media.timing import sample_boundary
    from copy import deepcopy
    start, end = 125, 471
    boundary = start + 173
    impulse = sample_boundary(boundary, 32000)
    p, ctx = prepared_project(tmp_path, end, sound=True, sample_rate=32000, impulses=[impulse])
    pd = p.to_dict(); first = pd['segments'][0]
    first['selected'] = False
    first['source_range'] = first['useful_range'] = {'start': 0, 'end': start}
    second = deepcopy(first)
    second.update(id='selected-scene', selected=True, boundary_before='cut', continuity_group_id='selected-shot')
    second['useful_range'] = second['source_range'] = {'start': start, 'end': end}
    pd['segments'].append(second); pd['windows'] = {}; pd['active_result_by_window'] = {}
    p = Project.from_dict(pd)
    p = apply_plan(p, plan_windows(resolve_project(p), RenderProfile.from_dict(profile()), context=ctx))
    p, results = cpu_results(p, ctx)
    with pytest.raises(ValueError, match='PARTIAL_RESULT'):
        assemble_export(p, results, AudioTimeline.from_dict(p['audio_timeline']), DEFAULT_POLICY, context=ctx)
    out = assemble_export(p, results, AudioTimeline.from_dict(p['audio_timeline']),
                          {**DEFAULT_POLICY, 'selection': 'selected'}, context=ctx)
    artifact = tmp_path / out.result['artifacts'][0]['locator']['path']
    decoded = array('h', command([ctx.versions['ffmpeg_path'], '-v', 'error', '-i', str(artifact), '-map', '0:a:0', '-f', 's16le', 'pipe:1']))
    assert len(decoded) == sample_boundary(end - start, 32000)
    assert [i for i, v in enumerate(decoded) if v] == [impulse - sample_boundary(start, 32000)]
    assert len(out.report['audio']['sample_phase_corrections']) <= 1
