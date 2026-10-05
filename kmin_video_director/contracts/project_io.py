"""Confined project I/O. No relink search, downloads or media decoding."""
import os
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from ..errors import ContractError, fail
from .records import Project, Settings
from .serialization import MAX_PROJECT_BYTES, canonical_bytes, digest_bytes, loads, parse_json
from .validation import validate_locator
from .confined_io import protected_parent, publication_lease


def resolve_locator(project_root, relative_path):
    validate_locator(relative_path)
    root = Path(project_root).resolve()
    path = root.joinpath(*relative_path.split("/")).resolve()
    if not path.is_relative_to(root) or path == root:
        fail("INVALID_LOCATOR", "The locator escapes the selected project folder.")
    return path


def _read(root, relative_path):
    try:
        with protected_parent(root, relative_path) as (parent, name):
            with parent.read(name) as stream:
                value = stream.read(MAX_PROJECT_BYTES + 1)
        if len(value) > MAX_PROJECT_BYTES:
            fail("RESOURCE_LIMIT", "Project JSON exceeds the 8 MiB limit.")
        return value
    except FileNotFoundError:
        fail("SOURCE_MISSING", "Project file is missing.", stage="load")
    except OSError:
        fail("PROJECT_IO_ERROR", "Project file cannot be read.", stage="load")


def load_project(project_root, relative_path):
    result = loads(_read(project_root, relative_path))
    if not isinstance(result, Project):
        fail("INVALID_RECORD", "The selected file must contain a Project.")
    return result


def save_project(project, project_root, relative_path, *, overwrite=False):
    if not isinstance(project, Project):
        fail("INVALID_RECORD", "Save requires a validated Project.")
    payload = canonical_bytes(project) + b"\n"
    if len(payload) > MAX_PROJECT_BYTES:
        fail("RESOURCE_LIMIT", "Project JSON exceeds the 8 MiB limit.")
    try:
        with protected_parent(project_root, relative_path, create=True) as (parent, name):
            temporary = None
            try:
                temporary = _stage_project(parent, payload)
                with publication_lease(parent, name):
                    # Compare after staging, under the same OS lease as publish.
                    # A newer successful interleaved save cannot be overwritten.
                    if parent.exists(name):
                        if not overwrite:
                            fail("TARGET_EXISTS", "Choose a new filename or explicitly enable overwrite.", stage="save")
                        with parent.read(name) as stream:
                            previous = loads(stream.read(MAX_PROJECT_BYTES + 1))
                        if not isinstance(previous, Project) or previous.id != project.id or project["revision"] < previous["revision"]:
                            fail("STALE_DEPENDENCY", "Overwrite requires the same project and a current revision.", stage="save")
                        if project != previous and project["revision"] == previous["revision"]:
                            fail("STALE_DEPENDENCY", "Saved edits must increment the project revision.", stage="save")
                    parent.publish(temporary, name, overwrite)
                    if overwrite: temporary = None
                return parent.path / name
            finally:
                if temporary is not None: parent.unlink(temporary)
    except FileExistsError:
        fail("TARGET_EXISTS", "The destination already exists.", stage="save")
    except ContractError:
        raise
    except OSError:
        fail("PROJECT_IO_ERROR", "Atomic project save failed; no partial file is activated.", stage="save")


def _stage_project(parent, payload):
    if os.name == "nt":
        stream = tempfile.NamedTemporaryFile(dir=parent.path, prefix=".kvd-", suffix=".partial", delete=False)
        name = Path(stream.name).name
    else:
        name = ".kvd-" + uuid.uuid4().hex + ".partial"
        fd = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=parent.fd)
        stream = os.fdopen(fd, "wb")
    try:
        with stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        return name
    except BaseException:
        parent.unlink(name)
        raise


@dataclass(frozen=True)
class ResolvedProject:
    project: Project
    settings: Mapping[str, Settings]
    origins: Mapping[str, Mapping[str, str]]
    assets_checked: bool = False


def resolve_project(project, *, asset_root=None, check_assets=False):
    if not isinstance(project, Project):
        fail("INVALID_RECORD", "Resolve requires a validated Project.")
    values, origins = {}, {}
    data = project.to_dict()
    for segment in data["segments"]:
        values[segment["id"]] = Settings.from_dict({**data["defaults"], **segment["overrides"]})
        origins[segment["id"]] = MappingProxyType({key: "segment" if key in segment["overrides"] else "default"
                                                 for key in data["defaults"]})
    if check_assets:
        if asset_root is None:
            fail("INVALID_LOCATOR", "Select a project asset folder for an explicit asset check.")
        import hashlib
        for media in data["media"].values():
            try:
                size, hash = 0, hashlib.sha256()
                with protected_parent(asset_root, media["locator"]["path"]) as (parent, name):
                    with parent.read(name) as stream:
                        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                            size += len(chunk)
                            hash.update(chunk)
            except OSError:
                fail("SOURCE_MISSING", "A listed asset cannot be opened.", details={"media_id": media["id"]})
            if size != media["fingerprint"]["byte_size"] or hash.hexdigest() != media["fingerprint"]["digest"]["hex"]:
                fail("SOURCE_CHANGED", "A listed asset differs from its recorded content.", details={"media_id": media["id"]})
    return ResolvedProject(project, MappingProxyType(values), MappingProxyType(origins), check_assets)


def migrate_v1_example(project_root, source_path, destination_path):
    """Only the documented unretimed, empty-ref v1 conformance shape is supported.

    There was no deployed v1 contract. Ambiguous refs, technical segments and
    existing render/analysis/state records require a separately designed profile.
    """
    source = resolve_locator(project_root, source_path)
    if source == resolve_locator(project_root, destination_path):
        fail("MIGRATION_UNSUPPORTED", "Migration must write a separate new file.")
    original = _read(project_root, source_path)
    data = parse_json(original)
    if (type(data) is not dict or data.get("kind") != "kmin.project" or data.get("schema_version") != "1.0.0"
            or type(data.get("defaults")) is not dict or data["defaults"].get("references") != []
            or any(data.get(name) for name in ("results", "windows", "active_result_by_window", "reference_bindings",
                                               "continuation_states", "prompt_recipes", "scene_analyses", "detection_proposals"))):
        fail("MIGRATION_UNSUPPORTED", "Input is outside the explicit v1-example migration profile.")
    try:
        data["schema_version"] = "2.0.0"
        data["defaults"]["reference_binding_ids"] = data["defaults"].pop("references")
        for media in data["media"].values():
            if media["locator"]["scheme"] != "relative":
                fail("MIGRATION_UNSUPPORTED", "Legacy absolute locators require explicit relinking.")
            validate_locator(media["locator"]["path"])
            media["locator"]["scheme"] = "project_relative"
        for segment in data["segments"]:
            if segment["boundary_type"] not in ("first", "cut", "continue") or "references" in segment["overrides"]:
                fail("MIGRATION_UNSUPPORTED", "Ambiguous technical boundaries/references need an explicit migration.")
            segment["useful_range"] = segment.pop("range")
            segment["source_range"] = dict(segment["useful_range"])
            segment["boundary_before"] = segment.pop("boundary_type")
            segment["schema_version"] = "2.0.0"
            segment.pop("resolved_settings_digest", None)
        for control in data["controls"].values():
            control["schema_version"] = "2.0.0"
        data.setdefault("extensions", {})["kvd.migration"] = {
            "profile": "kvd.v1-example/1", "from_version": "1.0.0", "to_version": "2.0.0",
            "source_digest": digest_bytes(original), "invalidated": ["windows", "results", "active_result_by_window"]}
        project = Project.from_dict(data)
    except (KeyError, TypeError, AttributeError):
        fail("MIGRATION_UNSUPPORTED", "Legacy input does not match the v1-example profile.")
    if _read(project_root, source_path) != original:
        fail("SOURCE_CHANGED", "Migration source changed; no new file was saved.")
    save_project(project, project_root, destination_path)
    return project
