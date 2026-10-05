import json
import threading
import tracemalloc

import pytest

from kmin_video_director.contracts.worker import ProjectLocator, StreamSelection
from tests.media.support import context, video, command, raw_video, backend_path


def test_actual_rotation_sar_portrait_and_off_grid_dimensions(tmp_path):
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    ctx = context(tmp_path)
    src = video(tmp_path, width=38, height=20, count=2)
    encoded = tmp_path / 'coded.mov'
    rotated = tmp_path / 'display rotation.mov'
    command([backend_path('ffmpeg'), '-v', 'error', '-i', str(src), '-c:v', 'libx264rgb',
        '-crf', '0', '-threads', '1', str(encoded)])
    command([backend_path('ffmpeg'), '-v', 'error', '-noautorotate', '-display_rotation', '90',
        '-i', str(encoded), '-c', 'copy', str(rotated)])
    found = probe_media(ProjectLocator(rotated.name), StreamSelection(), context=ctx)
    assert found.media['probe']['video']['rotation'] == 90
    out = normalize_media(found.media, DEFAULT_RECIPE, context=ctx)
    assert out.normalization['report']['display_dimensions'] == [20, 38]
    # Independent native displayed decoder is the orientation oracle. The owner
    # explicitly disables auto-rotate, applies its recorded transform exactly once.
    assert raw_video(tmp_path / out.media['locator']['path']) == raw_video(rotated)
    four_three = video(tmp_path, width=32, height=24, count=2, name='display-four-three.nut')
    out = normalize_media(probe_media(ProjectLocator(four_three.name), StreamSelection(), context=ctx).media,
        DEFAULT_RECIPE, context=ctx)
    assert out.normalization['report']['display_dimensions'] == [32, 24]
    assert raw_video(tmp_path / out.media['locator']['path']) == raw_video(four_three)
    sar = video(tmp_path, width=32, height=24, count=2, sar='4/3', name='four three.nut')
    out = normalize_media(probe_media(ProjectLocator(sar.name), StreamSelection(), context=ctx).media,
        DEFAULT_RECIPE, context=ctx)
    assert out.normalization['report']['display_dimensions'] == [43, 24]
    assert out.media['probe']['video']['sar'] == {'num': 1, 'den': 1}
    portrait = video(tmp_path, width=19, height=37, count=2, name='portrait.nut')
    out = normalize_media(probe_media(ProjectLocator(portrait.name), StreamSelection(), context=ctx).media,
        DEFAULT_RECIPE, context=ctx)
    assert out.normalization['report']['display_dimensions'] == [19, 37]


def test_owned_child_midflight_cancellation_and_disk_quota_remove_unpublished_output(tmp_path):
    from kmin_video_director.media.backend import process, Budget, target
    src = video(tmp_path)
    ctx = context(tmp_path)
    timer = threading.Timer(0.2, ctx.cancellation.cancel)
    timer.start()
    try:
        with pytest.raises(ValueError, match='CANCELLED'):
            with process([ctx.versions['ffmpeg_path'], '-v', 'error', '-re', '-stream_loop', '-1',
                '-i', str(src), '-an', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1'], ctx, Budget(ctx)) as child:
                child.stdout.read(1024**2)
        assert child.poll() is not None
    finally:
        timer.cancel(); timer.join()
    limited = context(tmp_path, disk_quota_bytes=1024)
    locator = {'scheme': 'project_relative', 'path': 'cache/quota-test.nut'}
    budget = Budget(limited)
    with pytest.raises(ValueError, match='RESOURCE_LIMIT'):
        with target(locator, limited, budget) as tmp:
            with process([limited.versions['ffmpeg_path'], '-v', 'error', '-y', '-stream_loop', '-1',
                '-i', str(src), '-t', '30', '-c:v', 'ffv1', '-threads', '1', '-f', 'nut', str(tmp)], limited, budget):
                pass
    assert not (tmp_path / locator['path']).exists()
    assert not list((tmp_path / 'cache').glob('*.partial'))


def test_measured_memory_does_not_grow_with_film_frame_count(tmp_path):
    from kmin_video_director.media.probe import probe_media
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    receipts = []
    for count in (24, 1000):
        root = tmp_path / str(count); root.mkdir()
        src = video(root, count=count)
        ctx = context(root)
        tracemalloc.start()
        found = probe_media(ProjectLocator(src.name), StreamSelection(), context=ctx)
        out = normalize_media(found.media, DEFAULT_RECIPE, context=ctx)
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        peaks = [r['peak_working_set_bytes'] for r in out.normalization['report']['processes']]
        receipts.append({'frames': count, 'dimensions': [37, 19], 'python_traced_peak_bytes': peak,
            'rgb_buffer_bound_bytes': out.normalization['report']['active_pixel_buffer_bound_bytes'],
            'backend_peak_working_set_bytes': peaks, 'disk_peak_bytes': out.normalization['report']['operation_disk_peak_bytes']})
        assert out.normalization['frame_count'] == count
        assert peak < 8 * 1024**2
        assert all(p is None or p < 256 * 1024**2 for p in peaks)
    assert receipts[1]['python_traced_peak_bytes'] <= receipts[0]['python_traced_peak_bytes'] + 1024**2
    print('MEMORY_RECEIPT ' + json.dumps(receipts, sort_keys=True))
