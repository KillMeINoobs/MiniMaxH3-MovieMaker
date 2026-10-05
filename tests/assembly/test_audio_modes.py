from array import array
import wave

import pytest

from kmin_video_director.contracts import AudioTimeline, Project, RenderResult
from tests.assembly.support import prepared_project, cpu_results
from tests.media.support import command


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
