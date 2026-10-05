import re
import uuid

from ..errors import fail
from ..version import SCHEMA_VERSION
from .serialization import digest_json
from .validation import validate_schema
from .specs import DIGEST

CACHE_LAYERS = frozenset({"temporal", "spatial", "control", "generation", "analysis", "prompt", "continuation", "assembly"})


def make_id(kind):
    if re.fullmatch(r"[a-z][a-z0-9_]{0,30}", kind) is None:
        fail("INVALID_RECORD", "Identifier prefix must be a stable lowercase kind.")
    return f"{kind}-{uuid.uuid4()}"


def stable_id(kind, *identity):
    if re.fullmatch(r"[a-z][a-z0-9_]{0,30}", kind) is None:
        fail("INVALID_RECORD", "Identifier prefix must be a stable lowercase kind.")
    return kind + "-" + digest_json({"schema_version": SCHEMA_VERSION, "identity": list(identity)})["hex"][:32]


def cache_key(layer, dependencies, *, algorithm_version):
    if layer not in CACHE_LAYERS or not algorithm_version:
        fail("INVALID_RECORD", "Cache keys need a known layer and explicit algorithm version.")
    def check(value):
        if type(value) is dict:
            if {"path", "locator", "mtime_ns"} & set(value):
                fail("INVALID_RECORD", "Cache identity uses content/version dependencies, not locators or mtime hints.")
            for child in value.values():
                check(child)
        elif type(value) in (list, tuple):
            for child in value:
                check(child)
    check(dependencies)
    return digest_json({"schema_version": SCHEMA_VERSION, "layer": layer,
                        "algorithm_version": algorithm_version, "dependencies": dependencies})


def cache_locator(layer, key, *, suffix="json"):
    if layer not in CACHE_LAYERS or re.fullmatch(r"[a-z0-9]{1,12}", suffix) is None:
        fail("INVALID_LOCATOR", "Cache layer or suffix is unsupported.")
    validate_schema(key, DIGEST)
    hex = key["hex"]
    return {"scheme": "project_relative", "path": f"cache/{layer}/2/{hex[:2]}/{hex}.{suffix}"}


def require_runtime_capabilities(*, operation=None, control=None, settings=None, window=None):
    # Store/round-trip future records; do not advertise unimplemented execution.
    if operation is not None:
        fail("UNSUPPORTED_CAPABILITY", "The foundation does not implement this runtime operation.", details={"operation": operation})
    if control is not None and control["type"] not in ("canny", "off"):
        fail("UNSUPPORTED_CAPABILITY", "Only Canny/off belong to the initial M1 runtime policy.")
    if settings is not None and (settings["reference_binding_ids"] or settings["continuity_policy"] == "carry"
                                  or settings["prompt_recipe_id"] is not None):
        fail("UNSUPPORTED_CAPABILITY", "Reference, analysis and carry execution are not implemented in M1.")
    if window is not None and window["context"]["mode"] != "none":
        fail("UNSUPPORTED_CAPABILITY", "M1 execution requires explicit no-context windows.")
