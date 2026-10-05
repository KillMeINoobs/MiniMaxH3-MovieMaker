import importlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from .example_data import project, window, control, result, future_records, HASH


def api():
    return importlib.import_module("kmin_video_director.contracts")


def test_immutable_unicode_roundtrip_and_future_minor():
    c = api()
    value = project()
    value["extensions"]["example.notes"] = {"text": "Папка с пробелами"}
    value["schema_version"] = "2.1.0"
    record = c.Project.from_dict(value)
    value["defaults"]["prompt"] = "mutated"
    assert record.to_dict()["defaults"]["prompt"] != "mutated"
    assert c.loads(c.dumps(record)).to_dict() == record.to_dict()
    copy = record.to_dict()
    copy["media"].clear()
    assert len(record.to_dict()["media"]) == 2
    assert "Папка" in c.dumps(record)


@pytest.mark.parametrize("path", ["../clip.mp4", "media/../clip.mp4", "/clip.mp4", "C:/clip.mp4",
    "C:clip.mp4", "\\\\host\\clip", "https://host/clip", "media\\clip", "a//b", "./b", "a/./b",
    "CON", "a/NUL.bin", "a/clip. ", "a/clip\x00.mp4"])
def test_bad_locators_rejected(path):
    c = api()
    data = project()
    data["media"]["media-source"]["locator"]["path"] = path
    with pytest.raises(c.ContractError) as error:
        c.Project.from_dict(data)
    assert error.value.code in {"INVALID_LOCATOR", "INVALID_RECORD"}


@pytest.mark.parametrize("mutation,code", [
    (lambda p: p.update(schema_version="3.0.0"), "UNSUPPORTED_SCHEMA_MAJOR"),
    (lambda p: p.update(required_features=["unknown/1"]), "UNSUPPORTED_REQUIRED_FEATURE"),
    (lambda p: p["defaults"].update(seed="18446744073709551616"), "INVALID_SEED"),
    (lambda p: p["defaults"].update(seed="-1"), "INVALID_RECORD"),
    (lambda p: p["defaults"].update(seed=43), "INVALID_RECORD"),
    (lambda p: p["media"]["media-source"]["fingerprint"]["digest"].update(hex="A" * 64), "INVALID_RECORD"),
    (lambda p: p["segments"][0]["useful_range"].update(start=1), "COVERAGE_MISMATCH"),
    (lambda p: p["segments"][0]["useful_range"].update(end=0), "INVALID_INTERVAL"),
    (lambda p: p.update(frame_count=True), "INVALID_RECORD"),
    (lambda p: p["defaults"].update(control_spec_id="missing"), "DANGLING_REFERENCE"),
    (lambda p: p["controls"]["ctrl-canny"].update(strength=float("nan")), "INVALID_JSON"),
    (lambda p: p["normalization"]["duration"].update(num=30, den=2), "INVALID_RATIONAL"),
    (lambda p: p["normalization"].update(frame_count=359), "FRAME_COUNT_MISMATCH"),
])
def test_rejections_have_stable_codes(mutation, code):
    c = api()
    data = project()
    mutation(data)
    with pytest.raises(c.ContractError) as error:
        c.Project.from_dict(data)
    assert error.value.code == code
    assert set(error.value.to_dict()) == {"code", "message", "stage", "retryable", "details"}


def test_window_semantics_and_no_runtime_future_features():
    c = api()
    good = c.GenerationWindow.from_dict(window())
    assert good.id == "win-1"
    for field, value in [("inference_frame_count", 362), ("inference_frame_count", 180),
                         ("output_useful_range", {"start": 0, "end": 179})]:
        data = window()
        data[field] = value
        with pytest.raises(c.ContractError):
            c.GenerationWindow.from_dict(data)
    data = window()
    data["input_spans"][1]["repeat_frame"] = 191
    with pytest.raises(c.ContractError):
        c.GenerationWindow.from_dict(data)
    data = control()
    data["type"] = "depth"
    stored = c.ControlSpec.from_dict(data)
    with pytest.raises(c.ContractError, match="UNSUPPORTED_CAPABILITY"):
        c.require_runtime_capabilities(control=stored)
    for name, data in future_records().items():
        assert c.loads(json.dumps(data)).to_dict() == data
    with pytest.raises(c.ContractError, match="UNSUPPORTED_CAPABILITY"):
        c.require_runtime_capabilities(operation="AnalyzeScene")


def test_no_fake_success_or_gpu_receipt():
    c = api()
    data = result()
    data["validation"]["gpu"] = "passed"
    with pytest.raises(c.ContractError):
        c.RenderResult.from_dict(data)
    data = result()
    data["status"] = "succeeded"
    with pytest.raises(c.ContractError, match="PARTIAL_RESULT"):
        c.RenderResult.from_dict(data)


def test_canonical_hash_inheritance_and_cache():
    c = api()
    p = c.Project.from_dict(project())
    resolved = c.resolve_project(p)
    assert resolved.settings["seg-1"].to_dict() == project()["defaults"]
    assert resolved.origins["seg-1"]["seed"] == "default"
    data = project()
    data["segments"][0]["overrides"] = {"seed": "42", "reference_binding_ids": []}
    r = c.resolve_project(c.Project.from_dict(data))
    assert r.settings["seg-1"]["seed"] == "42"
    assert r.origins["seg-1"]["reference_binding_ids"] == "segment"
    assert c.digest_json({"a": 1, "b": "я"}) == c.digest_json({"b": "я", "a": 1})
    assert c.digest_json([1, 2]) != c.digest_json([2, 1])
    assert c.cache_key("control", {"content": HASH}, algorithm_version="canny/1") == c.cache_key(
        "control", {"content": HASH}, algorithm_version="canny/1")
    with pytest.raises(c.ContractError):
        c.cache_key("control", {"path": "media/a"}, algorithm_version="canny/1")


def test_load_save_and_migration_preserve_original(tmp_path):
    c = api()
    p = c.Project.from_dict(project())
    path = c.save_project(p, tmp_path, "Папка/project.kvd.json")
    assert c.load_project(tmp_path, "Папка/project.kvd.json") == p
    before = path.read_bytes()
    with pytest.raises(c.ContractError, match="TARGET_EXISTS"):
        c.save_project(p, tmp_path, "Папка/project.kvd.json")
    assert path.read_bytes() == before
    v1 = project()
    v1["schema_version"] = "1.0.0"
    for seg in v1["segments"]:
        seg["range"] = seg.pop("useful_range")
        seg.pop("source_range")
        seg["boundary_type"] = seg.pop("boundary_before")
    for m in v1["media"].values():
        m["locator"]["scheme"] = "relative"
    v1["defaults"]["references"] = v1["defaults"].pop("reference_binding_ids")
    source = tmp_path / "original-v1.json"
    source.write_text(json.dumps(v1), encoding="utf-8")
    original = source.read_bytes()
    migrated = c.migrate_v1_example(tmp_path, "original-v1.json", "migrated.json")
    assert source.read_bytes() == original
    assert migrated.id == p.id
    assert migrated["extensions"]["kvd.migration"]["source_digest"] == c.digest_bytes(original)
    assert migrated["segments"][0]["id"] == p["segments"][0]["id"]
    with pytest.raises(c.ContractError):
        c.migrate_v1_example(tmp_path, "original-v1.json", "original-v1.json")


def test_loader_duplicate_keys_unknown_major_and_symlink_escape(tmp_path):
    c = api()
    with pytest.raises(c.ContractError, match="INVALID_JSON"):
        c.loads('{"kind":"kmin.project","kind":"kmin.segment"}')
    with pytest.raises(c.ContractError, match="UNSUPPORTED_SCHEMA_MAJOR"):
        c.loads('{"kind":"kmin.project","schema_version":"8.0.0","id":"future"}')
    external = tmp_path.parent / (tmp_path.name + "-external")
    external.mkdir()
    try:
        (tmp_path / "escape").symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("Host does not permit a symlink fixture")
    with pytest.raises(c.ContractError, match="INVALID_LOCATOR"):
        c.resolve_locator(tmp_path, "escape/project.json")


def test_schema_export_matches_and_independent_validator():
    c = api()
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from kmin_video_director.contracts.specs import SCHEMAS, BASE
    registry = Registry().with_resources((BASE + name + ".schema.json", Resource.from_contents(schema))
                                         for name, schema in SCHEMAS.items())
    cases = {"project": project(), "generation_window": window(), "control_spec": control(),
             "render_result": result(), **future_records()}
    for name, schema in SCHEMAS.items():
        Draft202012Validator.check_schema(schema)
        exported = Path("schemas") / (name + ".schema.json")
        assert json.loads(exported.read_text(encoding="utf-8")) == schema
    for name, data in cases.items():
        Draft202012Validator(SCHEMAS[name], registry=registry).validate(data)
        c.loads(json.dumps(data))
