import pytest

from kmin_video_director.contracts import RenderProfile, resolve_project
from kmin_video_director.contracts.worker import ProjectLocator, StreamSelection
from tests.contracts.example_data import profile
from tests.media.support import context, video, numbered_frame


def test_bounded_disk_window_padding_and_inverse_crop(tmp_path):
    from kmin_video_director.media.probe import probe_media, verify_cfr
    from kmin_video_director.media.normalize import normalize_media, DEFAULT_RECIPE
    from kmin_video_director.media.prepare import prepare_window
    from kmin_video_director.media.project import create_project, apply_plan
    from kmin_video_director.planning.windows import plan_windows
    from kmin_video_director.media.geometry import inverse_filter
    from tests.media.support import command
    src = video(tmp_path, count=6)
    ctx = context(tmp_path)
    m = probe_media(ProjectLocator(src.name), StreamSelection(), context=ctx).media
    normalized = normalize_media(m, DEFAULT_RECIPE, context=ctx)
    p = create_project(m, normalized, RenderProfile.from_dict(profile()), prompt='Visible authored text', seed='7')
    plan = plan_windows(resolve_project(p), RenderProfile.from_dict(profile()), context=ctx)
    p = apply_plan(p, plan)
    w = plan.windows[0]
    from kmin_video_director.contracts import SpatialTransform
    s = SpatialTransform.from_dict(p['spatial_transforms'][w['spatial_transform_id']])
    out = prepare_window(w, normalized.media, s, context=ctx)
    assert out.frame_count == 124 and out.window_id == w.id
    verify_cfr(out.media, 124, ctx)
    artifact = tmp_path / out.media['locator']['path']
    cropped = command([ctx.versions['ffmpeg_path'], '-v', 'error', '-i', str(artifact), '-vf', inverse_filter(s),
        '-pix_fmt', 'rgb24', '-fps_mode', 'passthrough', '-f', 'rawvideo', 'pipe:1'])
    assert cropped == b''.join(numbered_frame(i) for i in range(6)) + numbered_frame(5) * 118
    assert out.media['role'] == 'prepared_video'
    # Prompt/key edits do not invalidate source/spatial preparation.
    pd = p.to_dict()
    pd['segments'][0]['overrides']['prompt'] = 'Another visible prompt'
    from kmin_video_director.contracts import Project
    pd['windows'] = {}; pd['active_result_by_window'] = {}
    p2 = Project.from_dict(pd)
    plan2 = plan_windows(resolve_project(p2), RenderProfile.from_dict(profile()), context=ctx)
    out2 = prepare_window(plan2.windows[0], normalized.media, s, context=ctx)
    assert out2.media['fingerprint']['digest'] == out.media['fingerprint']['digest']
    assert plan2.windows[0]['generation_key'] != w['generation_key']


def test_ambiguous_eof_requires_explicit_policy(tmp_path, monkeypatch):
    from kmin_video_director.media import probe
    src = video(tmp_path, count=1, rate='120')
    original = probe._frame_lines
    def missing_duration(*args):
        for row in original(*args):
            row['duration'] = '0'
            yield row
    monkeypatch.setattr(probe, '_frame_lines', missing_duration)
    with pytest.raises(ValueError, match='AMBIGUOUS_MEDIA_TIMING'):
        probe.probe_media(ProjectLocator(src.name), StreamSelection(), context=context(tmp_path))
    out = probe.probe_media(ProjectLocator(src.name), StreamSelection(), context=context(tmp_path, endpoint_duration='1/120'))
    assert out.timing['endpoint_policy'] == 'explicit_final_frame_duration'
    assert out.timing['duration'] == {'num': 1, 'den': 120}
