"""Confined project I/O. No relink search, downloads or media decoding."""
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from ..errors import ContractError, fail
from .records import Project, Settings
from .serialization import MAX_PROJECT_BYTES, canonical_bytes, digest_bytes, loads, parse_json
from .validation import validate_locator


def resolve_locator(project_root, relative_path):
    validate_locator(relative_path)
    root = Path(project_root).resolve()
    path = root.joinpath(*relative_path.split("/")).resolve()
    if not path.is_relative_to(root) or path == root:
        fail("INVALID_LOCATOR", "The locator escapes the selected project folder.")
    return path


def _read(root, relative_path):
    path = resolve_locator(root, relative_path)
    try:
        with path.open("rb") as stream:
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
    path = resolve_locator(project_root, relative_path)
    payload = canonical_bytes(project) + b"\n"
    if len(payload) > MAX_PROJECT_BYTES:
        fail("RESOURCE_LIMIT", "Project JSON exceeds the 8 MiB limit.")
    temporary = None
    try:
        if path.exists():
            if not overwrite:
                fail("TARGET_EXISTS", "Choose a new project filename or explicitly enable overwrite.", stage="save")
            previous = load_project(project_root, relative_path)
            if previous.id != project.id or project["revision"] < previous["revision"]:
                fail("STALE_DEPENDENCY", "Overwrite requires the same project and a current revision.", stage="save")
            if project != previous and project["revision"] == previous["revision"]:
                fail("STALE_DEPENDENCY", "Saved edits must increment the project revision.", stage="save")
        path.parent.mkdir(parents=True, exist_ok=True)
        if resolve_locator(project_root, relative_path) != path:
            fail("INVALID_LOCATOR", "Project folder changed during save.")
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".kvd-", suffix=".partial", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(temporary, path)
            temporary = None
        else:
            # A complete file becomes visible atomically, without clobbering an
            # existing destination. Unsupported filesystems fail explicitly.
            os.link(temporary, path)
        return path
    except FileExistsError:
        fail("TARGET_EXISTS", "The destination already exists.", stage="save")
    except ContractError:
        raise
    except OSError:
        fail("PROJECT_IO_ERROR", "Atomic project save failed; no partial file is activated.", stage="save")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@dataclass(frozen=True)
class ResolvedProject:
    project: Project
    settings: object
    origins: object
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
            path = resolve_locator(asset_root, media["locator"]["path"])
            try:
                size, hash = 0, hashlib.sha256()
                with path.open("rb") as stream:
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
            or data.get("defaults", {}).get("references") != []
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
    except (KeyError, TypeError):
        fail("MIGRATION_UNSUPPORTED", "Legacy input does not match the v1-example profile.")
    if _read(project_root, source_path) != original:
        fail("SOURCE_CHANGED", "Migration source changed; no new file was saved.")
    save_project(project, project_root, destination_path)
    return project
