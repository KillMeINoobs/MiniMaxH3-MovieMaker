import json

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from kmin_video_director.contracts import Project, RenderResult, AudioTimeline
from kmin_video_director.contracts.specs import BASE
from tests.assembly.support import prepared_project, cpu_results
from tests.media.support import video


def test_actual_portable_output_matches_generated_schemas_and_explicit_selection(tmp_path):
    from kmin_video_director.assembly.selection import select_results
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    p, ctx = prepared_project(tmp_path, frames=6)
    p, results = cpu_results(p, ctx)
    empty = select_results(p, ())
    assert not empty['active_result_by_window']
    selected = select_results(empty, results)
    assert selected['active_result_by_window'] == p['active_result_by_window']
    with pytest.raises(ValueError, match='DUPLICATE_ID'):
        select_results(p, (*results, *results))
    stale = results[0].to_dict(); stale['generation_key']['hex'] = 'a' * 64
    with pytest.raises(ValueError, match='STALE_DEPENDENCY'):
        select_results(p, (RenderResult.from_dict(stale),))
    output = assemble_export(selected, results, AudioTimeline.from_dict(p['audio_timeline']), DEFAULT_POLICY, context=ctx)
    from pathlib import Path
    schemas = {f.name.removesuffix('.schema.json'): json.loads(f.read_text()) for f in Path('schemas').glob('*.schema.json')}
    registry = Registry().with_resources((BASE + n + '.schema.json', Resource.from_contents(s)) for n, s in schemas.items())
    records = [('project', selected.to_dict()), ('render_result', output.result.to_dict()),
        ('audio_timeline', p['audio_timeline'])]
    records += [('generation_window', w) for w in p['windows'].values()]
    records += [('spatial_transform', s) for s in p['spatial_transforms'].values()]
    records += [('media_ref', m) for m in p['media'].values()]
    records += [('media_ref', m) for m in output.result['artifacts']]
    for kind, data in records:
        Draft202012Validator(schemas[kind], registry=registry).validate(data)


def test_matching_bytes_with_false_pts_receipt_are_reprobed_and_rejected(tmp_path):
    from kmin_video_director.assembly.export import assemble_export, DEFAULT_POLICY
    from kmin_video_director.media.backend import hash_file
    p, ctx = prepared_project(tmp_path, frames=6)
    p, results = cpu_results(p, ctx)
    pd = p.to_dict(); result = results[0].to_dict()
    source = video(tmp_path, count=6, rate='12', name='false-timing.nut')
    artifact = result['artifacts'][0]
    artifact['locator']['path'] = source.name
    artifact['fingerprint'].update(digest=hash_file(source, ctx), byte_size=source.stat().st_size,
        mtime_ns=str(source.stat().st_mtime_ns))
    # All selected portable records agree, but actual decoded timing is different.
    pd['results'][result['id']] = result
    p = Project.from_dict(pd)
    with pytest.raises(ValueError, match='STALE_DEPENDENCY'):
        assemble_export(p, (RenderResult.from_dict(result),), AudioTimeline.from_dict(p['audio_timeline']),
            DEFAULT_POLICY, context=ctx)
