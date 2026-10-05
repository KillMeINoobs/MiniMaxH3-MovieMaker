"""CPU Project nodes. No model/media/queue imports or hidden execution."""
import json

from ..contracts import Project, ContractError, dumps, loads, load_project, save_project, resolve_project
from ..version import SCHEMA_VERSION


def report(project, *, code="STRUCTURE_VALID", assets_checked=False):
    return json.dumps({"code": code, "schema_version": SCHEMA_VERSION, "project_id": project.id,
                       "frame_count": project["frame_count"], "fps": 24,
                       "assets_checked": assets_checked, "gpu": "not_performed"}, ensure_ascii=False, sort_keys=True)


def output(project, *values, code="STRUCTURE_VALID"):
    text = report(project, code=code)
    return {"ui": {"kvd_report": [json.loads(text)]}, "result": (project, *values, text)}


def selected_root(value):
    if not value.strip():
        raise ContractError("INVALID_LOCATOR", "Select the local project folder explicitly.")
    return value


class ProjectJSON:
    CATEGORY = "KVD/Project"
    DESCRIPTION = "Load a portable project from JSON. Checks structure and references; does not open media or run models."
    RETURN_TYPES = ("KVD_PROJECT", "STRING", "STRING")
    RETURN_NAMES = ("project", "project_json", "validation_report")
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"project_json": ("STRING", {"default": "", "multiline": True,
            "tooltip": "Paste a kmin.project 2.x record. The JSON is saved with the workflow."})}}

    @classmethod
    def VALIDATE_INPUTS(cls, project_json):
        try:
            value = loads(project_json)
            if not isinstance(value, Project):
                return "INVALID_RECORD: Expected a Project record."
            return True
        except ContractError as error:
            return str(error)

    def execute(self, project_json):
        value = loads(project_json)
        if not isinstance(value, Project):
            raise ContractError("INVALID_RECORD", "Expected a Project record.")
        return output(value, dumps(value))


class LoadProject:
    CATEGORY = "KVD/Project"
    DESCRIPTION = "Load a project JSON inside the selected folder. Missing files give explicit errors; assets are not searched or decoded."
    RETURN_TYPES = ("KVD_PROJECT", "STRING", "STRING")
    RETURN_NAMES = ("project", "project_json", "validation_report")
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "project_root": ("STRING", {"default": "", "tooltip": "Local folder explicitly selected by you; keep private workflow paths local."}),
            "project_file": ("STRING", {"default": "project.kvd.json", "tooltip": "Project-relative filename, for example projects/scene.kvd.json."})}}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")  # Explicit reload rechecks file content; no mtime-only cache.

    def execute(self, project_root, project_file):
        project = load_project(selected_root(project_root), project_file)
        return output(project, dumps(project))


class SaveProject:
    CATEGORY = "KVD/Project"
    DESCRIPTION = "Atomically save a validated Project. Existing files are preserved unless overwrite is explicitly enabled; saved edits must advance revision."
    RETURN_TYPES = ("KVD_PROJECT", "STRING", "STRING")
    RETURN_NAMES = ("project", "saved_file", "validation_report")
    FUNCTION = "execute"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "project": ("KVD_PROJECT", {"tooltip": "Validated portable Project."}),
            "project_root": ("STRING", {"default": "", "tooltip": "Local project folder; no asset copies or uploads."}),
            "project_file": ("STRING", {"default": "project.kvd.json", "tooltip": "A normalized relative path inside this folder."}),
            "overwrite": ("BOOLEAN", {"default": False, "tooltip": "Explicitly replace only this project's file at a current revision."})}}

    def execute(self, project, project_root, project_file, overwrite=False):
        save_project(project, selected_root(project_root), project_file, overwrite=overwrite)
        return output(project, project_file, code="PROJECT_SAVED")


class ValidateProject:
    CATEGORY = "KVD/Project"
    DESCRIPTION = "Validate project structure and resolve inherited scene settings. This check does not execute media processing or generation."
    RETURN_TYPES = ("KVD_PROJECT", "STRING")
    RETURN_NAMES = ("project", "validation_report")
    FUNCTION = "execute"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"project": ("KVD_PROJECT", {"tooltip": "Connect a validated Project."})}}

    def execute(self, project):
        resolve_project(project)
        return output(project)


NODE_CLASS_MAPPINGS = {"KVD_ProjectJSON": ProjectJSON, "KVD_LoadProject": LoadProject,
                       "KVD_SaveProject": SaveProject, "KVD_ValidateProject": ValidateProject}
NODE_DISPLAY_NAME_MAPPINGS = {"KVD_ProjectJSON": "KVD Project · JSON", "KVD_LoadProject": "KVD Load Project",
                            "KVD_SaveProject": "KVD Save Project", "KVD_ValidateProject": "KVD Validate Project"}
