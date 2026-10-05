"""Offline structural validation plus cross-field invariants; never loads media/models."""
import math
import re
from fractions import Fraction

from ..errors import ContractError, fail
from .specs import MAX_INT, SCHEMAS, RANGE, RATIONAL, SETTINGS_FIELDS

SUPPORTED_FEATURES = frozenset({"portable_project/1", "cfr24/1", "h3_lattice/1", "structural_control/1"})


def validate_json(value, path="$", depth=0):
    if depth > 96:
        fail("RESOURCE_LIMIT", "JSON nesting exceeds the supported limit.", details={"field": path})
    if value is None or type(value) in (bool, str):
        return
    if type(value) is int:
        if abs(value) > MAX_INT:
            fail("INVALID_JSON", "Use safe JSON integers; seeds are decimal strings.", details={"field": path})
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) is list:
        for i, child in enumerate(value):
            validate_json(child, f"{path}[{i}]", depth + 1)
        return
    if type(value) is dict and all(type(k) is str for k in value):
        for key, child in value.items():
            validate_json(child, f"{path}.{key}", depth + 1)
        return
    fail("INVALID_JSON", "Expected finite JSON values.", details={"field": path})


def _json_equal(a, b):
    """JSON equality: booleans are distinct from numbers, including in objects."""
    if type(a) is bool or type(b) is bool:
        return type(a) is type(b) and a == b
    if type(a) in (int, float) and type(b) in (int, float):
        return a == b
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(_json_equal(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b))
    return a == b


def validate_schema(value, schema, path="$", document=None):
    """Validate exactly the declarative subset exported by specs.py, offline."""
    document = document or schema
    if "$ref" in schema:
        file, _, fragment = schema["$ref"].partition("#")
        target = SCHEMAS[file.removesuffix(".schema.json")] if file else document
        for part in fragment.strip("/").split("/") if fragment else ():
            target = target[part.replace("~1", "/").replace("~0", "~")]
        return validate_schema(value, target, path, SCHEMAS[file.removesuffix(".schema.json")] if file else document)
    for key in ("oneOf", "anyOf"):
        if key in schema:
            matches = 0
            for choice in schema[key]:
                try:
                    validate_schema(value, choice, path, document)
                    matches += 1
                except ContractError:
                    pass
            if matches < 1 or (key == "oneOf" and matches != 1):
                fail("INVALID_RECORD", "Value does not match the declared variants.", details={"field": path})
    types = {"object": lambda v: type(v) is dict, "array": lambda v: type(v) is list,
             "string": lambda v: type(v) is str, "integer": lambda v: type(v) is int,
             "number": lambda v: type(v) in (int, float), "boolean": lambda v: type(v) is bool,
             "null": lambda v: v is None}
    if "type" in schema and not types[schema["type"]](value):
        fail("INVALID_RECORD", "Incorrect JSON type.", details={"field": path, "expected": schema["type"]})
    if ("const" in schema and not _json_equal(value, schema["const"])
            or "enum" in schema and not any(_json_equal(value, v) for v in schema["enum"])):
        fail("INVALID_RECORD", "Value is outside the declared constants.", details={"field": path})
    if type(value) in (int, float):
        if "minimum" in schema and value < schema["minimum"] or "maximum" in schema and value > schema["maximum"]:
            fail("INVALID_RECORD", "Number is outside the declared bounds.", details={"field": path})
    if type(value) is str:
        if (len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", MAX_INT)
                or "pattern" in schema and re.search(schema["pattern"], value) is None):
            fail("INVALID_RECORD", "String does not match the declared format.", details={"field": path})
    if type(value) is list:
        if len(value) < schema.get("minItems", 0):
            fail("INVALID_RECORD", "Array is too short.", details={"field": path})
        if schema.get("uniqueItems") and any(any(_json_equal(item, v) for v in value[:i]) for i, item in enumerate(value)):
            fail("INVALID_RECORD", "Array contains duplicate entries.", details={"field": path})
        for i, item in enumerate(value):
            validate_schema(item, schema.get("items", {}), f"{path}[{i}]", document)
    if type(value) is dict:
        for key in schema.get("required", ()):
            if key not in value:
                fail("INVALID_RECORD", "Required field is missing.", details={"field": f"{path}.{key}"})
        for key, item in value.items():
            matched = []
            if key in schema.get("properties", {}):
                matched.append(schema["properties"][key])
            matched.extend(s for pattern, s in schema.get("patternProperties", {}).items() if re.search(pattern, key))
            if not matched:
                extra = schema.get("additionalProperties", True)
                if extra is False:
                    fail("INVALID_RECORD", "Unknown field; use namespaced extensions.", details={"field": f"{path}.{key}"})
                if type(extra) is dict:
                    matched.append(extra)
            for child_schema in matched:
                validate_schema(item, child_schema, f"{path}.{key}", document)


def validate_locator(path):
    if type(path) is not str or not path or re.search(r'[\x00-\x1f\x7f\\:< >"|?*]', path.replace(" ", "")):
        fail("INVALID_LOCATOR", "Use a normalized project-relative path.")
    parts = path.split("/")
    reserved = re.compile(r"^(con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?: *\..*)?$", re.I)
    if any(not p or p in (".", "..") or p.endswith((".", " ")) or reserved.fullmatch(p) for p in parts):
        fail("INVALID_LOCATOR", "Absolute paths, traversal and reserved names are not portable.")
    return path


def _walk_shared(value, schema, document=None):
    """Apply shared semantics only where the schema declares shared values.

    Owner reports, recipes, mode drafts and namespaced extensions remain opaque
    finite JSON. Their similarly named keys do not become contract fields.
    """
    document = document or schema
    if "$ref" in schema:
        file, _, fragment = schema["$ref"].partition("#")
        target = SCHEMAS[file.removesuffix(".schema.json")] if file else document
        for part in fragment.strip("/").split("/") if fragment else ():
            target = target[part.replace("~1", "/").replace("~0", "~")]
        return _walk_shared(value, target, SCHEMAS[file.removesuffix(".schema.json")] if file else document)
    for variant in ("oneOf", "anyOf"):
        if variant in schema:
            for choice in schema[variant]:
                try:
                    validate_schema(value, choice, document=document)
                except ContractError:
                    continue
                _walk_shared(value, choice, document)
                break
    if schema == SETTINGS_FIELDS["seed"] and int(value) > 2**64 - 1:
        fail("INVALID_SEED", "Seed must fit an unsigned 64-bit integer.")
    properties = schema.get("properties", {})
    if properties == RANGE["properties"] and value["start"] >= value["end"]:
        fail("INVALID_INTERVAL", "Half-open ranges require start < end.")
    if properties == RATIONAL["properties"] and math.gcd(value["num"], value["den"]) != 1:
        fail("INVALID_RATIONAL", "Rationals must be reduced.")
    if "scheme" in properties and properties["scheme"].get("const") == "project_relative":
        validate_locator(value["path"])
    if "kind" in properties and "schema_version" in properties:
        check_version(value)
    if type(value) is list and "items" in schema:
        for child in value:
            _walk_shared(child, schema["items"], document)
    if type(value) is dict:
        for key, child in value.items():
            child_schema = properties.get(key, schema.get("additionalProperties"))
            if type(child_schema) is dict:
                _walk_shared(child, child_schema, document)


def check_version(value):
    version = value.get("schema_version")
    if type(version) is not str or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is None:
        fail("INVALID_RECORD", "Expected a semantic schema version.")
    if version.split(".")[0] != "2":
        fail("UNSUPPORTED_SCHEMA_MAJOR", "This schema major needs an explicit migration.")
    features = value.get("required_features", [])
    if type(features) is not list or any(type(f) is not str for f in features):
        fail("INVALID_RECORD", "Required features must be an array of stable strings.")
    if set(features) - SUPPORTED_FEATURES:
        fail("UNSUPPORTED_REQUIRED_FEATURE", "The record requires an unavailable feature.")


def _length(r):
    return r["end"] - r["start"]


def _fraction(r):
    return Fraction(r["num"], r["den"])


def _coverage(ranges, start, end):
    cursor = start
    for r in ranges:
        if r["start"] != cursor:
            fail("COVERAGE_MISMATCH", "Ordered ranges must cover the interval exactly once.")
        cursor = r["end"]
    if cursor != end:
        fail("COVERAGE_MISMATCH", "Ordered ranges do not reach the required endpoint.")


def validate_window(w):
    n = w["inference_frame_count"]
    if not 124 <= n <= 345 or (n - 5) % 17:
        fail("FRAME_COUNT_MISMATCH", "M1 inference count must be 124..345 on the 17k+5 lattice.")
    output = w["output_useful_range"]
    if output["end"] > n or _length(output) != _length(w["useful_range"]):
        fail("FRAME_COUNT_MISMATCH", "Local useful output must match global useful coverage.")
    spans = w["input_spans"]
    _coverage([s["inference_range"] for s in spans], 0, n)
    useful = [s for s in spans if s["role"] == "useful"]
    _coverage([s["source_range"] for s in useful], w["useful_range"]["start"], w["useful_range"]["end"])
    _coverage([s["inference_range"] for s in useful], output["start"], output["end"])
    for s in useful:
        if _length(s["source_range"]) != _length(s["inference_range"]):
            fail("FRAME_COUNT_MISMATCH", "Useful input and source spans must have equal lengths.")
    for s in spans:
        if s["role"] == "padding" and not output["start"] <= s["repeat_frame"] < output["end"]:
            fail("INVALID_INTERVAL", "Padding must repeat a useful prepared frame.")
    c, p = w["context"], w["padding"]
    for role, counts in (("context", c), ("padding", p)):
        actual = {"before": 0, "after": 0}
        for span in (s for s in spans if s["role"] == role):
            interval = span["inference_range"]
            if interval["end"] <= output["start"]:
                actual["before"] += _length(interval)
            elif interval["start"] >= output["end"]:
                actual["after"] += _length(interval)
            else:
                fail("FRAME_COUNT_MISMATCH", "Context and padding must lie outside useful output.")
            if role == "context" and (span["continuation_state_id"] != c["continuation_state_id"]
                    or _length(span["source_range"]) != _length(interval)):
                fail("CONTINUATION_INCOMPATIBLE", "Context must identify and map the declared predecessor state.")
        if any(actual[side] != counts[side] for side in actual):
            fail("FRAME_COUNT_MISMATCH", "Context/padding counts must match their declared head or tail.")
    if output["start"] != c["before"] + p["before"] or n - output["end"] != c["after"] + p["after"]:
        fail("FRAME_COUNT_MISMATCH", "Useful trim must account for every head/tail frame.")
    if c["mode"] == "none" and (c["before"] or c["after"] or c["dependency_result_ids"] or c["continuation_state_id"]):
        fail("CONTINUATION_INCOMPATIBLE", "No-context mode cannot carry predecessor state.")
    from .serialization import digest_json
    if digest_json(w["resolved_settings"]) != w["resolved_settings_digest"]:
        fail("STALE_DEPENDENCY", "Window settings digest does not match its frozen settings.")
    for key in ("control_spec_id", "render_profile_id", "prompt_recipe_id"):
        if w[key] != w["resolved_settings"][key]:
            fail("STALE_DEPENDENCY", "Window settings and links disagree.")
    if len({r["socket"] for r in w["reference_manifest"]}) != len(w["reference_manifest"]):
        fail("REFERENCE_CONFLICT", "Reference sockets must be unique.")


def validate_result(r):
    v = r["validation"]
    if v["gpu"] != "not_performed" and (v["evidence_kind"] != "real_gpu" or not v["receipts"]):
        fail("INVALID_EVIDENCE", "GPU claims require real GPU receipts.")
    if r["progress"]["done"] > r["progress"]["total"]:
        fail("INVALID_RECORD", "Progress exceeds its total.")
    if r["status"] in ("succeeded", "passthrough"):
        if not r["artifacts"] or r["coverage"] is None or not v["receipts"] or r["error"] is not None:
            fail("PARTIAL_RESULT", "Success requires artifacts, exact coverage and validation receipts.")
        coverage = r["coverage"]
        if any(a["availability"] != "available" for a in r["artifacts"]):
            fail("PARTIAL_RESULT", "Success artifacts must be available.")
        if (coverage["decoded_frames"] != coverage["requested_frames"]
                or coverage["useful_frames"] != _length(coverage["useful_range"])
                or coverage["useful_frames"] != _length(coverage["output_useful_range"])
                or coverage["output_useful_range"]["end"] > coverage["decoded_frames"]
                or coverage["fps"] != {"num": 24, "den": 1}
                or not coverage["padding_removed"] or not coverage["context_removed"]):
            fail("FRAME_COUNT_MISMATCH", "Successful output has inconsistent useful coverage.")


def validate_profile(p):
    if (p["fps"] != {"num": 24, "den": 1} or p["lattice"] != {"offset": 5, "step": 17}
            or p["shape_min"] != 5 or p["policy_inference_min"] != 124
            or p["policy_inference_max"] != 345 or p["grid"] != 32
            or p["policy_duration_max"] != {"num": 15, "den": 1}):
        fail("UNSUPPORTED_CAPABILITY", "This foundation implements the explicit M1 native profile policy.")
    if p["evidence"] != "source_only" and not p["receipts"]:
        fail("INVALID_EVIDENCE", "Verified profiles need attached receipts.")


def validate_project(p):
    f, norm = p["frame_count"], p["normalization"]
    d = _fraction(norm["duration"])
    if d <= 0:
        fail("AMBIGUOUS_MEDIA_TIMING", "Source presentation span must be positive.")
    rounded = (d.numerator * 48 + d.denominator) // (2 * d.denominator)
    expected = max(1, rounded)
    clamp = norm["duration_clamp"]
    if (f != expected or norm["frame_count"] != f or norm["rounded_frame_count"] != rounded
            or clamp != {"applied": rounded == 0, "reason": "minimum_one_frame" if rounded == 0 else None,
                         "before_frame_count": rounded, "after_frame_count": expected}
            or _fraction(norm["duration_error"]) != Fraction(f, 24) - d):
        fail("FRAME_COUNT_MISMATCH", "CFR24 duration, rounding and clamp provenance disagree.")
    segments = p["segments"]
    _coverage([s["useful_range"] for s in segments], 0, f)
    if len({s["id"] for s in segments}) != len(segments):
        fail("DUPLICATE_ID", "Segment IDs must be unique.")
    for name in ("media", "controls", "render_profiles", "results", "detection_proposals", "scene_analyses",
                 "prompt_recipes", "subjects", "reference_bindings", "continuation_states", "windows", "spatial_transforms"):
        for id, value in p.get(name, {}).items():
            if id != value["id"]:
                fail("DUPLICATE_ID", "Registry keys must match stable record IDs.", details={"registry": name})
            if "project_id" in value and value["project_id"] != p["id"]:
                fail("DANGLING_REFERENCE", "A nested record belongs to another project.")
    def link(id, registry):
        if id not in registry:
            fail("DANGLING_REFERENCE", "A referenced ID is missing from its registry.")
        return registry[id]
    source = link(p["source_media_id"], p["media"])
    canonical = link(p["canonical_media_id"], p["media"])
    if source["role"] != "source_video" or canonical["role"] != "prepared_video":
        fail("DANGLING_REFERENCE", "Source and canonical media must have distinct declared roles.")
    by_segment = {s["id"]: s for s in segments}
    previous = None
    groups = set()
    for s in segments:
        if s["project_id"] != p["id"] or s["source_media_id"] != p["canonical_media_id"]:
            fail("DANGLING_REFERENCE", "Segments must refer to this project's canonical media.")
        if s["source_range"] != s["useful_range"]:
            fail("COVERAGE_MISMATCH", "Initial M1 segments are unretimed canonical ranges.")
        boundary, group = s["boundary_before"], s["continuity_group_id"]
        if (previous is None and boundary != "first" or previous is not None and boundary == "first"
                or boundary == "continue" and group != previous["continuity_group_id"]
                or boundary in ("first", "cut") and group in groups):
            fail("CONTINUATION_INCOMPATIBLE", "Cuts start new continuity groups; continuation stays inside a shot.")
        groups.add(group)
        previous = s
        effective = {**p["defaults"], **s["overrides"]}
        _check_settings_links(effective, p, s, link)
        from .serialization import digest_json
        if s.get("resolved_settings_digest", digest_json(effective)) != digest_json(effective):
            fail("STALE_DEPENDENCY", "Segment settings digest is stale.")
        for id in s["analysis_ids"]:
            link(id, p["scene_analyses"])
        for id in s["prompt_draft_ids"]:
            link(id, p["prompt_recipes"])
    _check_settings_links(p["defaults"], p, None, link)
    audio = p["audio_timeline"]
    if audio["sample_count"] != (f * audio["sample_rate"] + 12) // 24:
        fail("AUDIO_SYNC_MISMATCH", "Audio samples must use absolute frame boundaries.")
    if audio["source_media_id"] is not None:
        link(audio["source_media_id"], p["media"])
    for decision in audio["decisions"]:
        link(decision["segment_id"], by_segment)
    for control in p["controls"].values():
        validate_semantics("control_spec", control)
        for id in control["compatibility"]["profile_ids"]:
            link(id, p["render_profiles"])
    for profile in p["render_profiles"].values():
        validate_profile(profile)
    for transform in p.get("spatial_transforms", {}).values():
        validate_semantics("spatial_transform", transform)
    for m in p["media"].values():
        validate_semantics("media_ref", m)
    for b in p["reference_bindings"].values():
        link(b["subject_id"], p["subjects"])
        image = link(b["image_media_id"], p["media"])
        if image["role"] != "reference_image" or image["fingerprint"]["digest"] != b["content_digest"]:
            fail("REFERENCE_CONFLICT", "Appearance bindings must identify the exact approved reference image.")
        for id in b["segment_ids"]:
            link(id, by_segment)
    for name in ("scene_analyses", "prompt_recipes", "continuation_states", "windows", "results"):
        for record in p.get(name, {}).values():
            if record.get("segment_id") is not None:
                link(record["segment_id"], by_segment)
            validate_semantics(record["kind"].removeprefix("kmin."), record)
    for w in p.get("windows", {}).values():
        seg = link(w["segment_id"], by_segment)
        if not seg["useful_range"]["start"] <= w["useful_range"]["start"] < w["useful_range"]["end"] <= seg["useful_range"]["end"]:
            fail("COVERAGE_MISMATCH", "Window useful range lies outside its editorial segment.")
        link(w["spatial_transform_id"], p.get("spatial_transforms", {}))
        _check_settings_links(w["resolved_settings"], p, seg, link)
        if w["resolved_settings"] != {**p["defaults"], **seg["overrides"]}:
            fail("STALE_DEPENDENCY", "Frozen window settings differ from current effective segment settings.")
        for span in w["input_spans"]:
            if span["role"] == "useful":
                media = link(span["media_id"], p["media"])
                if media["id"] != seg["source_media_id"] or media["role"] != "prepared_video":
                    fail("DANGLING_REFERENCE", "Useful input must identify the segment's canonical source.")
    for window_id, result_id in p["active_result_by_window"].items():
        w = link(window_id, p.get("windows", {}))
        r = link(result_id, p["results"])
        if r["window_id"] != window_id or r["status"] not in ("succeeded", "passthrough"):
            fail("PARTIAL_RESULT", "Only explicit completed matching results may be active.")
        if r["segment_id"] != w["segment_id"] or r["generation_key"] != w["generation_key"]:
            fail("STALE_DEPENDENCY", "Active output must match the current window, scene and generation key.")
        coverage = r["coverage"]
        spatial = link(w["spatial_transform_id"], p.get("spatial_transforms", {}))
        passthrough = r["status"] == "passthrough"
        if passthrough and not by_segment[w["segment_id"]]["passthrough"]:
            fail("PARTIAL_RESULT", "Source passthrough must be explicitly selected by the segment.")
        expected_local = {"start": 0, "end": _length(w["useful_range"])} if passthrough else w["output_useful_range"]
        expected_count = _length(w["useful_range"]) if passthrough else w["inference_frame_count"]
        if (coverage["useful_range"] != w["useful_range"] or coverage["output_useful_range"] != expected_local
                or coverage["requested_frames"] != expected_count or coverage["decoded_frames"] != expected_count
                or coverage["width"] != spatial["output_width"] or coverage["height"] != spatial["output_height"]):
            fail("COVERAGE_MISMATCH", "Active output coverage and dimensions must match its exact window mapping.")


def _check_settings_links(settings, project, segment, link):
    control = link(settings["control_spec_id"], project["controls"])
    link(settings["render_profile_id"], project["render_profiles"])
    if control["type"] != "off" and settings["render_profile_id"] not in control["compatibility"]["profile_ids"]:
        fail("MODEL_INCOMPATIBLE", "The selected control does not declare compatibility with this render profile.")
    for id in settings["reference_binding_ids"]:
        binding = link(id, project["reference_bindings"])
        if not binding["approved"] or segment and segment["id"] not in binding["segment_ids"]:
            fail("REFERENCE_UNBOUND", "Effective appearance bindings need explicit approval and scene presence.")
    recipe_id = settings["prompt_recipe_id"]
    if recipe_id is not None:
        recipe = link(recipe_id, project["prompt_recipes"])
        if (segment is None or recipe["status"] != "accepted" or recipe["segment_id"] != segment["id"]
                or recipe["segment_revision"] != segment["revision"]
                or recipe["accepted"] is None or recipe["accepted"]["text"] != settings["prompt"]
                or recipe["reference_binding_ids"] != settings["reference_binding_ids"]):
            fail("STALE_DEPENDENCY", "Only a matching accepted scene recipe may supply effective text.")
        for id in recipe["analysis_ids"]:
            analysis = link(id, project["scene_analyses"])
            if (analysis["segment_id"] != segment["id"] or analysis["segment_revision"] != segment["revision"]
                    or analysis["source_digest"] != project["media"][project["canonical_media_id"]]["fingerprint"]["digest"]):
                fail("STALE_DEPENDENCY", "Accepted recipe analysis dependencies are stale.")


def validate_semantics(name, data):
    if name == "project":
        validate_project(data)
    elif name == "generation_window":
        validate_window(data)
    elif name == "render_result":
        validate_result(data)
    elif name == "render_profile":
        validate_profile(data)
    elif name == "media_ref":
        if (data["availability"] == "available") != (data["error"] is None):
            fail("INVALID_RECORD", "Missing/changed assets need an explicit error.")
        for stream in ("video", "audio"):
            probe = data["probe"][stream]
            selected = data["fingerprint"][stream + "_stream"]
            if (probe is None) != (selected is None) or probe is not None and probe["stream_index"] != selected:
                fail("AMBIGUOUS_MEDIA_TIMING", "Probed streams must match the selected fingerprint streams.")
    elif name == "spatial_transform":
        rect = data["content_rect"]
        if (data["canvas_width"] % 32 or data["canvas_height"] % 32
                or rect["x"] + rect["width"] > data["canvas_width"]
                or rect["y"] + rect["height"] > data["canvas_height"]
                or rect["width"] != data["fitted_width"] or rect["height"] != data["fitted_height"]):
            fail("UNSUPPORTED_EXPORT_DIMENSIONS", "Shared content rectangle must fit the exact grid-aligned canvas.")
    elif name == "control_spec":
        if data["schedule"]["start_percent"] > data["schedule"]["end_percent"]:
            fail("INVALID_RECORD", "Denoising schedule must be ordered.")
        if data["type"] == "canny":
            params = data["backend"]["parameters"]
            low, high = params.get("low_threshold"), params.get("high_threshold")
            if data["backend"]["id"] != "comfy-native-canny" or type(low) not in (int, float) or type(high) not in (int, float) or not 0 <= low <= high <= 1:
                fail("UNSUPPORTED_CAPABILITY", "M1 Canny uses native 0..1 ordered thresholds.")
    elif name == "prompt_recipe":
        from .serialization import digest_bytes
        required = ({"integrated_multimodal_description", "overall_soundscape", "non_diegetic_music"}
                    if data["format_id"] == "h3.base/1" else
                    {"subject_definitions", "summary", "retention_analysis", "detailed_description", "overall_soundscape", "non_diegetic_music"})
        if set(data["blocks"]) != required:
            fail("PROMPT_INVALID", "Prompt block names must match the declared format.")
        if data["text_digest"] != digest_bytes(data["final_text"].encode("utf-8")):
            fail("PROMPT_INVALID", "Prompt text digest is inconsistent.")
        if data["status"] == "accepted":
            accepted = data["accepted"]
            if accepted is None or accepted["text"] != data["final_text"] or accepted["digest"] != data["text_digest"] or accepted["revision"] != data["revision"]:
                fail("PROMPT_INVALID", "Accepted text/revision/hash must be frozen together.")
    elif name == "detection_proposal":
        if data["state"] in ("accepted", "adjusted") and data["accepted_boundary"] is None:
            fail("INVALID_RECORD", "Accepted detection proposals need an explicit boundary.")
    elif name == "continuation_state":
        if data["video_tail_range"]["end"] != data["last_useful_local_end"] or _length(data["video_tail_range"]) != data["overlap_frames"]:
            fail("CONTINUATION_TAIL_UNMAPPED", "Continuation tail must end at the mapped last useful frame.")
        if data["validity"] == "valid" and (data["evidence"] != "gpu_verified" or not data["artifacts"]):
            fail("CONTINUATION_INCOMPATIBLE", "Valid runtime carry requires real verified state artifacts.")


def validate_record(name, data):
    validate_json(data)
    if type(data) is dict and "kind" in data:
        check_version(data)
    validate_schema(data, SCHEMAS[name])
    _walk_shared(data, SCHEMAS[name])
    validate_semantics(name, data)
