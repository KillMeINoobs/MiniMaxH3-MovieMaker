"""Independent-review regressions use synthetic JSON and temporary files only."""
from copy import deepcopy
from contextlib import contextmanager
import json
import os
from pathlib import Path
import stat
from types import SimpleNamespace

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


@pytest.mark.parametrize("hook", ["stage_project", "named_temporary"])
def test_interleaved_staging_cannot_overwrite_a_newer_revision(tmp_path, monkeypatch, hook):
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


@pytest.mark.parametrize("entrypoint", ["save", "load", "migration", "locator", "asset_check"])
def test_cyclic_selected_root_is_typed_redacted_and_does_not_mutate(tmp_path, entrypoint):
    validated = Project.from_dict(project())
    original = io.save_project(validated, tmp_path, "project.json").read_bytes()
    first, second = tmp_path / "a", tmp_path / "b"
    first.symlink_to(second, target_is_directory=True)
    second.symlink_to(first, target_is_directory=True)
    actions = {
        "save": lambda: io.save_project(validated, first, "project.json"),
        "load": lambda: io.load_project(first, "project.json"),
        "migration": lambda: io.migrate_v1_example(first, "project.json", "migrated.json"),
        "locator": lambda: io.resolve_locator(first, "project.json"),
        "asset_check": lambda: io.resolve_project(validated, asset_root=first, check_assets=True),
    }
    names_before = sorted(path.name for path in tmp_path.iterdir())
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR") as error:
        actions[entrypoint]()
    assert str(tmp_path) not in json.dumps(error.value.to_dict())
    assert str(tmp_path) not in str(error.value)
    assert error.value.__suppress_context__  # Raw resolver diagnostics must not leak in a traceback.
    assert (tmp_path / "project.json").read_bytes() == original
    assert sorted(path.name for path in tmp_path.iterdir()) == names_before
    assert not list(tmp_path.glob(".kvd-*.partial"))


@pytest.mark.parametrize("entrypoint", ["locator", "migration_source", "migration_destination"])
def test_cyclic_locator_resolution_is_typed_and_preserves_original(tmp_path, entrypoint):
    original = io.save_project(Project.from_dict(project()), tmp_path, "project.json").read_bytes()
    first, second = tmp_path / "a", tmp_path / "b"
    first.symlink_to(second, target_is_directory=True)
    second.symlink_to(first, target_is_directory=True)
    actions = {
        "locator": lambda: io.resolve_locator(tmp_path, "a/project.json"),
        "migration_source": lambda: io.migrate_v1_example(tmp_path, "a/project.json", "migrated.json"),
        "migration_destination": lambda: io.migrate_v1_example(tmp_path, "project.json", "a/migrated.json"),
    }
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR") as error:
        actions[entrypoint]()
    assert str(tmp_path) not in json.dumps(error.value.to_dict())
    assert error.value.__suppress_context__
    assert (tmp_path / "project.json").read_bytes() == original
    assert not (tmp_path / "migrated.json").exists()
    assert not list(tmp_path.glob(".kvd-*.partial"))


def test_invalid_selected_root_type_uses_the_shared_io_error(tmp_path):
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR") as error:
        io.save_project(Project.from_dict(project()), None, "project.json")
    assert error.value.__suppress_context__
    assert not list(tmp_path.iterdir())


def test_selected_project_folder_must_already_exist(tmp_path):
    selected = tmp_path / "missing folder"
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR"):
        io.resolve_locator(selected, "project.json")
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR"):
        io.save_project(Project.from_dict(project()), selected, "project.json")
    assert not selected.exists()


def test_nonregular_input_is_rejected_before_open(tmp_path, monkeypatch):
    """Synthetic stat result; this is not a POSIX FIFO runtime receipt."""
    from kmin_video_director.contracts.confined_io import Parent
    selected = tmp_path / "special.json"
    selected.write_bytes(b"synthetic")
    actual_stat, actual_open = Path.stat, Path.open
    def special_stat(path, *args, **kwargs):
        if path == selected:
            return SimpleNamespace(st_mode=stat.S_IFIFO)
        return actual_stat(path, *args, **kwargs)
    def reject_open(path, *args, **kwargs):
        if path == selected:
            raise AssertionError("A nonregular input must be rejected before opening")
        return actual_open(path, *args, **kwargs)
    monkeypatch.setattr(Path, "stat", special_stat)
    monkeypatch.setattr(Path, "open", reject_open)
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR"):
        with Parent(tmp_path).read("special.json"):
            pass


@pytest.mark.skipif(os.name != "posix", reason="POSIX FIFO runtime NOT PERFORMED on Windows")
def test_posix_fifo_input_is_rejected_as_nonregular(tmp_path):
    os.mkfifo(tmp_path / "project.json")
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR"):
        io.load_project(tmp_path, "project.json")


@pytest.mark.parametrize("kind,code", [("missing", "SOURCE_MISSING"),
    ("malformed", "INVALID_JSON"), ("directory", "PROJECT_IO_ERROR")])
def test_normal_load_errors_are_typed_and_leave_input_unchanged(tmp_path, kind, code):
    selected = tmp_path / "project.json"
    if kind == "malformed": selected.write_bytes(b"{malformed")
    if kind == "directory": selected.mkdir()
    with pytest.raises(ContractError, match=code) as error:
        io.load_project(tmp_path, "project.json")
    assert str(tmp_path) not in json.dumps(error.value.to_dict())
    if kind == "malformed": assert selected.read_bytes() == b"{malformed"
    if kind == "directory": assert not list(selected.iterdir())
    if kind == "missing": assert not selected.exists()


@pytest.mark.parametrize("failure", ["read", "stage", "publish"])
def test_ordinary_io_failures_preserve_old_project_and_cleanup(tmp_path, monkeypatch, failure):
    from kmin_video_director.contracts.confined_io import Parent
    selected = io.save_project(Project.from_dict(project()), tmp_path, "project.json")
    original = selected.read_bytes()
    def denied(*args, **kwargs):
        raise PermissionError("Synthetic ordinary I/O failure at " + str(tmp_path))
    if failure == "read": monkeypatch.setattr(Parent, "read", denied)
    if failure == "stage": monkeypatch.setattr(io.tempfile, "NamedTemporaryFile", denied)
    if failure == "publish": monkeypatch.setattr(Parent, "publish", denied)
    p2 = project(); p2["revision"] = 2
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR") as error:
        io.save_project(Project.from_dict(p2), tmp_path, "project.json", overwrite=True)
    assert str(tmp_path) not in json.dumps(error.value.to_dict())
    assert error.value.__suppress_context__
    assert selected.read_bytes() == original
    assert not list(tmp_path.glob(".kvd-*.partial"))


def test_committed_save_is_not_reported_failed_on_late_cleanup_error(tmp_path, monkeypatch, caplog):
    selected = io.save_project(Project.from_dict(project()), tmp_path, "project.json")
    actual_lease = io.publication_lease
    @contextmanager
    def late_cleanup_failure(*args, **kwargs):
        with actual_lease(*args, **kwargs):
            yield
        raise OSError("Synthetic cleanup failure at " + str(tmp_path))
    monkeypatch.setattr(io, "publication_lease", late_cleanup_failure)
    p2 = project(); p2["revision"] = 2
    updated = Project.from_dict(p2)
    assert io.save_project(updated, tmp_path, "project.json", overwrite=True) == selected
    assert io.load_project(tmp_path, "project.json") == updated
    assert not list(tmp_path.glob(".kvd-*.partial"))
    assert "committed" in caplog.text
    assert str(tmp_path) not in caplog.text


def test_unreadable_folder_resolution_has_a_typed_redacted_error(tmp_path, monkeypatch):
    def denied(*args, **kwargs):
        raise PermissionError("Synthetic folder permission error at " + str(tmp_path))
    monkeypatch.setattr(Path, "is_dir", denied)
    with pytest.raises(ContractError, match="PROJECT_IO_ERROR") as error:
        io.resolve_locator(tmp_path, "project.json")
    assert str(tmp_path) not in json.dumps(error.value.to_dict())
    assert error.value.__suppress_context__


@pytest.mark.parametrize("change", ["older", "same_revision_edits", "other_project"])
def test_rejected_overwrite_preserves_current_project(tmp_path, change):
    current = project(); current["revision"] = 2
    selected = io.save_project(Project.from_dict(current), tmp_path, "project.json")
    original = selected.read_bytes()
    candidate = deepcopy(current)
    if change == "older": candidate["revision"] = 1
    if change == "same_revision_edits": candidate["defaults"]["seed"] = "43"
    if change == "other_project":
        candidate["id"] = "project-other"
        for segment in candidate["segments"]:
            segment["project_id"] = candidate["id"]
    validated_candidate = Project.from_dict(candidate)
    with pytest.raises(ContractError, match="STALE_DEPENDENCY"):
        io.save_project(validated_candidate, tmp_path, "project.json", overwrite=True)
    assert selected.read_bytes() == original
    assert not list(tmp_path.glob(".kvd-*.partial"))
