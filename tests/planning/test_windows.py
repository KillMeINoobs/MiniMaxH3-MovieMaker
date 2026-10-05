from fractions import Fraction

import pytest

from kmin_video_director.contracts import Project, RenderProfile, resolve_project
from kmin_video_director.contracts.worker import CancellationFlag, OperationContext
from tests.contracts.example_data import project, profile


def snapshot(length, split=None):
    p = project()
    p['frame_count'] = length
    p['normalization'].update(duration={'num': length, 'den': 24}, frame_count=length,
        rounded_frame_count=length, duration_error={'num': 0, 'den': 1},
        duration_clamp={'applied': False, 'reason': None, 'before_frame_count': length,
                        'after_frame_count': length})
    # Reduced rationals are an actual shared contract requirement.
    d = Fraction(length, 24)
    p['normalization']['duration'] = {'num': d.numerator, 'den': d.denominator}
    p['audio_timeline']['sample_count'] = length * 2000
    p['windows'] = {}
    p['results'] = {}
    p['active_result_by_window'] = {}
    p['segments'][0]['useful_range'] = p['segments'][0]['source_range'] = {'start': 0, 'end': length}
    if split:
        from copy import deepcopy
        first = p['segments'][0]
        first['useful_range'] = first['source_range'] = {'start': 0, 'end': split}
        first['selected'] = False
        second = deepcopy(first)
        second.update(id='scene-two', boundary_before='cut', continuity_group_id='shot-two', selected=True)
        second['useful_range'] = second['source_range'] = {'start': split, 'end': length}
        p['segments'].append(second)
    return resolve_project(Project.from_dict(p))


@pytest.mark.parametrize('length,useful,native', [
    (1, [1], [124]), (346, [173, 173], [175, 175]),
    (360, [180, 180], [192, 192]), (1000, [334, 333, 333], [345, 345, 345])])
def test_exact_native_window_examples(tmp_path, length, useful, native):
    from kmin_video_director.planning.windows import plan_windows
    s = snapshot(length)
    out = plan_windows(s, RenderProfile.from_dict(profile()),
        context=OperationContext(tmp_path, CancellationFlag(), {}))
    assert [w['useful_range']['end'] - w['useful_range']['start'] for w in out.windows] == useful
    assert [w['inference_frame_count'] for w in out.windows] == native
    cursor = 0
    for w in out.windows:
        assert w['useful_range']['start'] == cursor
        cursor = w['useful_range']['end']
        assert w['context'] == {'mode': 'none', 'before': 0, 'after': 0,
            'dependency_result_ids': [], 'continuation_state_id': None}
        assert w['reference_manifest'] == []
    assert cursor == length
    assert not list(tmp_path.iterdir())
    assert s.project['segments'][0]['id'] == 'seg-1'


def test_selected_scene_stays_exact_and_preserves_editorial_records(tmp_path):
    from kmin_video_director.planning.windows import plan_windows
    s = snapshot(469, split=123)
    before = s.project.to_dict()
    out = plan_windows(s, RenderProfile.from_dict(profile()),
        context=OperationContext(tmp_path, CancellationFlag(), {}))
    assert [(w['useful_range']['start'], w['useful_range']['end']) for w in out.windows] == [(123, 296), (296, 469)]
    assert {w['segment_id'] for w in out.windows} == {'scene-two'}
    assert s.project.to_dict() == before


def test_planning_cancellation(tmp_path):
    from kmin_video_director.planning.windows import plan_windows
    c = CancellationFlag()
    c.cancel()
    with pytest.raises(ValueError, match='CANCELLED'):
        plan_windows(snapshot(360), RenderProfile.from_dict(profile()), context=OperationContext(tmp_path, c, {}))


def test_install_plan_can_save_a_revision_and_unchanged_replan_keeps_windows(tmp_path):
    from kmin_video_director.planning.windows import plan_windows
    from kmin_video_director.media.project import apply_plan
    from kmin_video_director.contracts import save_project, load_project
    original = snapshot(360).project
    save_project(original, tmp_path, 'project.json')
    ctx = OperationContext(tmp_path, CancellationFlag(), {})
    planned = apply_plan(original, plan_windows(resolve_project(original), RenderProfile.from_dict(profile()), context=ctx))
    assert planned['revision'] > original['revision']
    save_project(planned, tmp_path, 'project.json', overwrite=True)
    loaded = load_project(tmp_path, 'project.json')
    assert loaded == planned
    repeated = apply_plan(loaded, plan_windows(resolve_project(loaded), RenderProfile.from_dict(profile()), context=ctx))
    assert repeated == planned
