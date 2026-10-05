from copy import deepcopy
from pathlib import Path
import json
import pytest

from kmin_video_director.contracts import Project, GenerationWindow, ContractError, load_project, resolve_project
from .example_data import project, window


def test_padding_roles_match_their_declared_side():
    w = window()
    # Same aggregate counts, wrong placement: the padding is before the useful
    # content, while metadata claims tail padding.
    w["input_spans"] = [
        {"role":"padding","inference_range":{"start":0,"end":12},"repeat_frame":20},
        {"role":"useful","inference_range":{"start":12,"end":192},"media_id":"media-cfr",
         "source_range":{"start":0,"end":180}}]
    w["output_useful_range"] = {"start":12,"end":192}
    w["context"].update(mode="previous_generated",before=12,dependency_result_ids=["result-0"],continuation_state_id="state-0")
    w["padding"].update(before=0,after=0)
    # Aggregate context count mismatch is caught too.
    with pytest.raises(ContractError):
        GenerationWindow.from_dict(w)
    # Swap context/pad roles with equal counts but incorrect before/after maps.
    w["input_spans"] = [
        {"role":"padding","inference_range":{"start":0,"end":6},"repeat_frame":20},
        {"role":"useful","inference_range":{"start":6,"end":186},"media_id":"media-cfr",
         "source_range":{"start":0,"end":180}},
        {"role":"context","inference_range":{"start":186,"end":192},"continuation_state_id":"state-0",
         "tail_map_id":"tail-0","source_range":{"start":0,"end":6}}]
    w["output_useful_range"] = {"start":6,"end":186}
    w["context"].update(before=6,after=0)
    w["padding"].update(before=0,after=6)
    with pytest.raises(ContractError):
        GenerationWindow.from_dict(w)


def test_control_profile_compatibility_and_source_stream_closure():
    p = project()
    p["controls"]["ctrl-canny"]["compatibility"]["profile_ids"] = []
    with pytest.raises(ContractError, match="MODEL_INCOMPATIBLE"):
        Project.from_dict(p)
    p = project()
    p["media"]["media-source"]["fingerprint"]["video_stream"] = 2
    with pytest.raises(ContractError):
        Project.from_dict(p)


def test_asset_hash_verification_is_explicit_and_listed(tmp_path):
    p = Project.from_dict(project())
    assert resolve_project(p).assets_checked is False
    with pytest.raises(ContractError, match="SOURCE_MISSING"):
        resolve_project(p, asset_root=tmp_path, check_assets=True)


def test_all_exported_conformance_files_independent():
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from kmin_video_director.contracts.specs import SCHEMAS, BASE
    from kmin_video_director.contracts.validation import validate_record
    registry = Registry().with_resources((BASE + n + ".schema.json",Resource.from_contents(s)) for n,s in SCHEMAS.items())
    files = sorted(Path('tests/contracts/fixtures').glob('*.json'))
    assert len(files) == 15
    for file in files:
        data = json.loads(file.read_text(encoding='utf-8'))
        Draft202012Validator(SCHEMAS[file.stem],registry=registry).validate(data)
        validate_record(file.stem, data)
    assert Path('workflows/foundation_project.json').read_bytes() == Path('web/examples/foundation_project.json').read_bytes()
