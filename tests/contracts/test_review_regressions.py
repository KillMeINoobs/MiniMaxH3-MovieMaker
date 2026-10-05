"""Independent-review regressions use synthetic JSON and temporary files only."""
from copy import deepcopy
import json
import sys

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from kmin_video_director.contracts import ContractError, Project, SceneAnalysis
from kmin_video_director.contracts import project_io as io
from kmin_video_director.contracts.specs import BASE, SCHEMAS
from kmin_video_director.contracts.validation import validate_schema
from .example_data import HASH, future_records, media, project, result, window, profile


def project_with_active_synthetic_manifest():
    p, w, r = project(), window(), result()
    artifact = media("render-synthetic", "render_video")
    artifact.update(availability="available", error=None)
    r.update(status="succeeded", stage="trim", artifacts=[artifact], coverage={
        "useful_range": {"start": 0, "end": 180}, "output_useful_range": {"start": 0, "end": 180},
        "requested_frames": 192, "decoded_frames": 192, "useful_frames": 180,
        "width": 640, "height": 360, "fps": {"num": 24, "den": 1},
        "padding_removed": True, "context_removed": True, "pts_digest": deepcopy(HASH)})
    r["validation"]["receipts"] = ["Synthetic manifest conformance; no generation or media execution."]
    p["windows"], p["results"] = {w["id"]: w}, {r["id"]: r}
    p["active_result_by_window"] = {w["id"]: r["id"]}
    return p


@pytest.mark.parametrize("change", [
    lambda p: p["results"]["result-1"].update(generation_key={"algorithm": "sha256", "hex": "cd" * 32}),
    lambda p: (p["results"]["result-1"].update(window_id="missing-window"),
               p.update(active_result_by_window={"missing-window": "result-1"})),
    lambda p: p["results"]["result-1"]["coverage"].update(useful_range={"start": 180, "end": 360}),
    lambda p: p["windows"]["win-1"]["input_spans"][0].update(media_id="missing-media"),
    lambda p: p["results"]["result-1"]["coverage"].update(width=608),
    lambda p: p["segments"][0]["overrides"].update(seed="43"),
    lambda p: p["results"]["result-1"].update(status="passthrough"),
])
def test_active_output_and_input_dependency_closure(change):
    p = project_with_active_synthetic_manifest()
    Project.from_dict(p)  # Structural example only; no real output is claimed.
    change(p)
    with pytest.raises(ContractError):
        Project.from_dict(p)


@pytest.mark.parametrize("field", ["seed", "digest", "id", "version", "extension"])
def test_canonical_string_boundaries_match_independent_schema(field):
    p = project()
    if field == "seed": p["defaults"]["seed"] = "42\n"
    if field == "digest": p["media"]["media-source"]["fingerprint"]["digest"]["hex"] += "\n"
    if field == "id": p["id"] += "\n"
    if field == "version": p["schema_version"] += "\n"
    if field == "extension": p["extensions"]["owner.data\n"] = {}
    registry = Registry().with_resources((BASE + n + ".schema.json", Resource.from_contents(s))
                                        for n, s in SCHEMAS.items())
    assert not Draft202012Validator(SCHEMAS["project"], registry=registry).is_valid(p)
    with pytest.raises(ContractError):
        Project.from_dict(p)


def test_json_boolean_const_is_not_a_numeric_one():
    p = future_records()["scene_analysis"]
    p["no_inferred_transcript"] = 1
    with pytest.raises(ContractError, match="INVALID_RECORD"):
        SceneAnalysis.from_dict(p)
    for value, schema in ((True, {"const": 1}), (False, {"enum": [0]}), (1, {"enum": [True]})):
        with pytest.raises(ContractError): validate_schema(value, schema)
    validate_schema(1.0, {"const": 1})  # JSON numeric equality remains numeric.


def test_owner_report_json_is_opaque_but_finite():
    p = project()
    p["normalization"]["report"].update(seed="owner-specific", custom={"start": "text", "end": 1},
        rational={"num": "label", "den": "label"}, kind="owner.event", schema_version="n/a")
    assert Project.from_dict(p).to_dict() == p
    p["normalization"]["report"]["value"] = float("nan")
    with pytest.raises(ContractError, match="INVALID_JSON"):
        Project.from_dict(p)


def test_frozen_window_profile_control_and_effective_settings_close():
    from kmin_video_director.contracts import digest_json
    p, w, second = project(), window(), profile()
    second["id"] = "profile-two"
    p["render_profiles"][second["id"]] = second
    w["render_profile_id"] = w["resolved_settings"]["render_profile_id"] = second["id"]
    w["resolved_settings_digest"] = digest_json(w["resolved_settings"])
    p["windows"] = {w["id"]: w}
    with pytest.raises(ContractError, match="MODEL_INCOMPATIBLE"):
        Project.from_dict(p)
    p["controls"]["ctrl-canny"]["compatibility"]["profile_ids"].append(second["id"])
    with pytest.raises(ContractError, match="STALE_DEPENDENCY"):
        Project.from_dict(p)


def test_malformed_migration_returns_typed_error_and_preserves_source(tmp_path):
    for defaults in ([], "text", None, 1):
        source = tmp_path / "legacy.json"
        original = json.dumps({"kind": "kmin.project", "schema_version": "1.0.0", "defaults": defaults}).encode()
        source.write_bytes(original)
        with pytest.raises(ContractError, match="MIGRATION_UNSUPPORTED"):
            io.migrate_v1_example(tmp_path, "legacy.json", "migrated.json")
        assert source.read_bytes() == original
        assert not (tmp_path / "migrated.json").exists()


@pytest.mark.skipif(sys.platform != "win32", reason="Actual Windows directory sharing guarantee")
def test_actual_windows_parent_swap_before_staging_is_denied(tmp_path, monkeypatch):
    root, outside = tmp_path / "root", tmp_path / "outside"
    inside = root / "inside"
    inside.mkdir(parents=True); outside.mkdir()
    original_stage = io.tempfile.NamedTemporaryFile
    def swap_then_stage(*args, **kwargs):
        inside.rename(root / "original-inside")
        inside.symlink_to(outside, target_is_directory=True)
        return original_stage(*args, **kwargs)
    monkeypatch.setattr(io.tempfile, "NamedTemporaryFile", swap_then_stage)
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR"):
        io.save_project(Project.from_dict(project()), root, "inside/project.json")
    assert inside.is_dir() and not inside.is_symlink()
    assert not list(outside.iterdir())
    assert not (inside / "project.json").exists()


@pytest.mark.parametrize("hook", ["stage_project", "named_temporary"])
def test_interleaved_staging_cannot_overwrite_a_newer_revision(tmp_path, monkeypatch, hook):
    if hook == "named_temporary" and sys.platform != "win32":
        pytest.skip("Original review hook targets Windows NamedTemporaryFile staging")
    p1, p2, p3 = project(), project(), project()
    p2.update(revision=2); p2["defaults"]["seed"] = "2"
    p3.update(revision=3); p3["defaults"]["seed"] = "3"
    io.save_project(Project.from_dict(p1), tmp_path, "project.json")
    owner, attribute = (io, "_stage_project") if hook == "stage_project" else (io.tempfile, "NamedTemporaryFile")
    original_stage = getattr(owner, attribute)
    interleaved = False
    def newer_then_stage(*args, **kwargs):
        nonlocal interleaved
        if not interleaved:
            interleaved = True
            io.save_project(Project.from_dict(p3), tmp_path, "project.json", overwrite=True)
        return original_stage(*args, **kwargs)
    monkeypatch.setattr(owner, attribute, newer_then_stage)
    with pytest.raises(ContractError, match="STALE_DEPENDENCY"):
        io.save_project(Project.from_dict(p2), tmp_path, "project.json", overwrite=True)
    assert io.load_project(tmp_path, "project.json")["revision"] == 3
    assert not list(tmp_path.glob(".kvd-*.partial"))


@pytest.mark.skipif(sys.platform != "win32", reason="Actual Windows directory sharing guarantee")
def test_actual_windows_parent_swap_at_publish_preserves_original(tmp_path, monkeypatch):
    from kmin_video_director.contracts.confined_io import Parent
    root, outside = tmp_path / "root", tmp_path / "outside"
    inside = root / "inside"
    inside.mkdir(parents=True); outside.mkdir()
    before = io.save_project(Project.from_dict(project()), root, "inside/project.json").read_bytes()
    p2 = project(); p2["revision"] = 2
    def swap_at_publish(*args):
        inside.rename(root / "original-inside")
        inside.symlink_to(outside, target_is_directory=True)
        raise AssertionError("Protected Windows parent was replaced")
    monkeypatch.setattr(Parent, "publish", swap_at_publish)
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR"):
        io.save_project(Project.from_dict(p2), root, "inside/project.json", overwrite=True)
    assert (inside / "project.json").read_bytes() == before
    assert not list(outside.iterdir())
    assert not list(inside.glob(".kvd-*.partial"))


def test_failed_staging_keeps_original_and_sanitizes_error(tmp_path, monkeypatch):
    before = io.save_project(Project.from_dict(project()), tmp_path, "project.json").read_bytes()
    p2 = project(); p2["revision"] = 2
    def fail_flush(*args): raise OSError("private filesystem diagnostic")
    monkeypatch.setattr(io.os, "fsync", fail_flush)
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR") as error:
        io.save_project(Project.from_dict(p2), tmp_path, "project.json", overwrite=True)
    assert "private filesystem" not in str(error.value)
    assert (tmp_path / "project.json").read_bytes() == before
    assert not list(tmp_path.glob(".kvd-*.partial"))


def test_publication_lease_prevents_interleaving_after_revision_check(tmp_path, monkeypatch):
    from kmin_video_director.contracts.confined_io import Parent
    p1, p2, p3 = project(), project(), project()
    p2.update(revision=2); p3.update(revision=3)
    io.save_project(Project.from_dict(p1), tmp_path, "project.json")
    original_publish = Parent.publish
    calls = []
    def interleaved_publish(parent, temporary, name, overwrite):
        with pytest.raises(ContractError, match="PROJECT_BUSY") as error:
            io.save_project(Project.from_dict(p3), tmp_path, "project.json", overwrite=True)
        assert error.value.retryable is True
        calls.append("newer_save_deferred")
        return original_publish(parent, temporary, name, overwrite)
    with monkeypatch.context() as scoped:
        scoped.setattr(Parent, "publish", interleaved_publish)
        io.save_project(Project.from_dict(p2), tmp_path, "project.json", overwrite=True)
    assert calls == ["newer_save_deferred"]
    io.save_project(Project.from_dict(p3), tmp_path, "project.json", overwrite=True)
    assert io.load_project(tmp_path, "project.json")["revision"] == 3
    assert not list(tmp_path.glob(".kvd-*.partial"))


@pytest.mark.parametrize("name", ["COM¹.txt", "LPT².bin", "COM1 .txt"])
def test_additional_portable_windows_device_names_are_rejected(tmp_path, name):
    with pytest.raises(ContractError, match="INVALID_LOCATOR"):
        io.resolve_locator(tmp_path, name)
