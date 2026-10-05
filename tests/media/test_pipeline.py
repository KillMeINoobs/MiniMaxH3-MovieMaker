from fractions import Fraction
import json
import wave
from array import array

import pytest

from kmin_video_director.contracts import ContractError
from kmin_video_director.contracts.worker import ProjectLocator, StreamSelection
from tests.media.support import context, numbered_frame, raw_video, video, with_audio


@pytest.mark.parametrize('rate,count,expected', [('60', 6, [0, 2]), ('30000/1001', 7, [0, 1, 2, 3, 4, 6])])
def test_real_fractional_drop_and_exact_cfr_pts(tmp_path, rate, count, expected):
    from kmin_video_director.media.probe import probe_media, frame_rows
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    src = video(tmp_path, rate=rate, count=count)
    ctx = context(tmp_path)
    found = probe_media(ProjectLocator(src.name), StreamSelection(), context=ctx)
    out = normalize_media(found.media, DEFAULT_RECIPE, context=ctx)
    actual = raw_video(tmp_path / out.media['locator']['path'])
    assert actual == b''.join(numbered_frame(i) for i in expected)
    rows = list(frame_rows(out.media, ctx))
    tb = out.media['probe']['video']['time_base']
    assert [Fraction(r['pts'] * tb['num'], tb['den']) for r in rows] == [Fraction(j, 24) for j in range(len(expected))]
    assert out.normalization['frame_count'] == len(expected)
    assert out.audio_timeline['source_media_id'] is None


def test_actual_vfr_gap_selection_manifest_and_eof_clamp(tmp_path):
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    src = video(tmp_path, count=4, rate='120', pts=[0, 4, 13, 18])
    ctx = context(tmp_path)
    found = probe_media(ProjectLocator(src.name), StreamSelection(), context=ctx)
    assert found.media['probe']['video']['vfr']
    out = normalize_media(found.media, DEFAULT_RECIPE, context=ctx)
    assert raw_video(tmp_path / out.media['locator']['path']) == b''.join(numbered_frame(i) for i in [0, 1, 1, 2])
    manifest = tmp_path / out.normalization['report']['selection_manifest']['path']
    assert [json.loads(line)['source_frame'] for line in manifest.read_text().splitlines()] == [0, 1, 1, 2]
    assert out.normalization['report']['duplicated_frames'] == 1
    tiny = video(tmp_path, count=1, rate='120', name='tiny.nut')
    tiny_out = normalize_media(probe_media(ProjectLocator(tiny.name), StreamSelection(), context=ctx).media,
                               DEFAULT_RECIPE, context=ctx)
    assert tiny_out.normalization['duration_clamp']['applied']
    assert tiny_out.normalization['duration_error'] == {'num': 1, 'den': 30}


@pytest.mark.parametrize('origin,offset,expected_offset,expected_impulses', [
    (0, '0.0833333333333', Fraction(1, 12), [4000, 8000, 12000]),
    (2, '0', Fraction(-1, 12), [0, 4000])])
def test_global_pcm_retains_relative_audio_origin(tmp_path, origin, offset, expected_offset, expected_impulses):
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    clip = video(tmp_path, count=8, origin=origin)
    src = with_audio(tmp_path, clip, offset=offset)
    ctx = context(tmp_path)
    found = probe_media(ProjectLocator(src.name), StreamSelection(video=0, audio=1), context=ctx)
    out = normalize_media(found.media, DEFAULT_RECIPE, context=ctx)
    r = out.audio_timeline['source_offset']
    assert Fraction(r['num'], r['den']) == expected_offset
    with wave.open(str(tmp_path / out.normalization['report']['pcm_media']['locator']['path'])) as wav:
        assert wav.getnframes() == out.audio_timeline['sample_count'] == 16000
        data = array('h', wav.readframes(wav.getnframes()))
    assert [i for i, v in enumerate(data) if v] == expected_impulses


def test_missing_changed_nonregular_cancelled_and_quota(tmp_path):
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    ctx = context(tmp_path)
    with pytest.raises(ContractError, match='SOURCE_MISSING'):
        probe_media(ProjectLocator('missing.nut'), StreamSelection(), context=ctx)
    (tmp_path / 'folder').mkdir()
    with pytest.raises(ContractError, match='PROJECT_IO_ERROR'):
        probe_media(ProjectLocator('folder'), StreamSelection(), context=ctx)
    src = video(tmp_path)
    found = probe_media(ProjectLocator(src.name), StreamSelection(), context=ctx)
    with pytest.raises(ContractError, match='RESOURCE_LIMIT'):
        normalize_media(found.media, DEFAULT_RECIPE, context=context(tmp_path, disk_quota_bytes=16))
    with pytest.raises(ContractError, match='RESOURCE_LIMIT'):
        normalize_media(found.media, DEFAULT_RECIPE, context=context(tmp_path, working_set_bytes=20))
    ctx.cancellation.cancel()
    with pytest.raises(ContractError, match='CANCELLED'):
        probe_media(ProjectLocator(src.name), StreamSelection(), context=ctx)
    src.write_bytes(src.read_bytes() + b'changed')
    with pytest.raises(ContractError, match='SOURCE_CHANGED'):
        normalize_media(found.media, DEFAULT_RECIPE, context=context(tmp_path))
