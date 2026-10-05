"""Single declarative source for bundled/exported Draft 2020-12 schemas.

The runtime supports only the keywords used here, without network resolution.
Relational invariants are additionally checked by validation.py.
"""
BASE = "https://kmin-video-director.invalid/schemas/2.0.0/"
DRAFT = "https://json-schema.org/draft/2020-12/schema"
MAX_INT = 9007199254740991


def obj(properties, optional=(), *, extra=False):
    return {"type": "object", "properties": properties,
            "required": [k for k in properties if k not in optional], "additionalProperties": extra}


def array(items, **kwargs):
    return {"type": "array", "items": items, **kwargs}


def enum(*values):
    return {"enum": list(values)}


def ref(name):
    return {"$ref": "common.schema.json#/$defs/" + name}


def record_ref(name):
    return {"$ref": name + ".schema.json"}


def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def mapping(schema):
    return {"type": "object", "additionalProperties": schema}


TEXT = {"type": "string"}
BOOL = {"type": "boolean"}
INTEGER = {"type": "integer", "minimum": -MAX_INT, "maximum": MAX_INT}
COUNT = {**INTEGER, "minimum": 0}
POSITIVE = {**INTEGER, "minimum": 1}
NUMBER = {"type": "number"}
UNIT = {"type": "number", "minimum": 0, "maximum": 1}
JSON_OBJECT = {"type": "object"}
ID = {"type": "string", "minLength": 1, "maxLength": 96, "pattern": r"^[^\x00-\x1f\x7f]+(?![\s\S])"}
IDS = array(ID, uniqueItems=True)
RANGE = obj({"start": COUNT, "end": COUNT})
RATIONAL = obj({"num": INTEGER, "den": POSITIVE})
DIGEST = obj({"algorithm": {"const": "sha256"},
              "hex": {"type": "string", "pattern": r"^[0-9a-f]{64}(?![\s\S])"}})
LOCATOR = obj({"scheme": {"const": "project_relative"}, "path": {"type": "string", "minLength": 1}})
ERROR = obj({"code": ID, "message": TEXT, "stage": ID, "retryable": BOOL, "details": JSON_OBJECT})
EXTENSIONS = {"type": "object", "patternProperties": {r"^[A-Za-z][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)+(?![\s\S])": {}},
              "additionalProperties": False}
SETTINGS_FIELDS = {
    "prompt": TEXT, "prompt_recipe_id": nullable(ID),
    "seed": {"type": "string", "pattern": r"^(0|[1-9][0-9]{0,19})(?![\s\S])"},
    "control_spec_id": ID, "audio_mode": enum("preserve", "generate", "mute"),
    "reference_binding_ids": IDS, "continuity_policy": enum("none", "reset", "carry"),
    "spatial_policy": enum("preserve_display_pad", "draft_fit"), "render_profile_id": ID,
}
SETTINGS = obj(SETTINGS_FIELDS)
OVERRIDES = obj(SETTINGS_FIELDS, optional=tuple(SETTINGS_FIELDS))
EVIDENCE = enum("source_only", "load_verified", "gpu_verified")
PIN = obj({"id": ID, "version": ID, "model_digest": nullable(DIGEST)}, optional=("model_digest",))
SOCKET = obj({"binding_id": ID, "subject_id": ID, "media_id": ID, "content_digest": DIGEST,
              "socket": ID, "label": ID, "role": enum("identity", "appearance", "costume", "object", "style")})
VIDEO_PROBE = obj({"codec": ID, "stream_index": COUNT, "time_base": RATIONAL, "first_pts": INTEGER,
    "end_pts": INTEGER, "pts_digest": DIGEST, "rate": RATIONAL, "vfr": BOOL, "width": POSITIVE,
    "height": POSITIVE, "rotation": NUMBER, "sar": RATIONAL, "display_matrix": array(NUMBER),
    "color": TEXT, "pixel_format": TEXT})
AUDIO_PROBE = obj({"codec": ID, "stream_index": COUNT, "time_base": RATIONAL, "first_pts": INTEGER,
    "sample_rate": POSITIVE, "channels": POSITIVE, "skip_samples": COUNT}, optional=("skip_samples",))
MEDIA = obj({"id": ID, "role": enum("source_video", "reference_image", "reference_video", "reference_audio",
    "prepared_video", "control_map", "render_video", "audio_pcm"), "locator": LOCATOR,
    "fingerprint": obj({"digest": DIGEST, "byte_size": COUNT,
        "mtime_ns": {"type": "string", "pattern": r"^(0|[1-9][0-9]*)(?![\s\S])"},
        "video_stream": nullable(COUNT), "audio_stream": nullable(COUNT),
        "probe_version": ID, "decoder_version": ID}),
    "probe": obj({"video": nullable(VIDEO_PROBE), "audio": nullable(AUDIO_PROBE)}),
    "availability": enum("available", "missing", "changed"), "error": nullable(ERROR)})
SPATIAL = obj({"id": ID, "version": ID, "coded_width": POSITIVE, "coded_height": POSITIVE,
    "source_sar": RATIONAL, "display_matrix": array(NUMBER), "display_width": POSITIVE,
    "display_height": POSITIVE, "scale": RATIONAL, "fitted_width": POSITIVE, "fitted_height": POSITIVE,
    "canvas_width": POSITIVE, "canvas_height": POSITIVE,
    "content_rect": obj({"x": COUNT, "y": COUNT, "width": POSITIVE, "height": POSITIVE}),
    "pad_fill": JSON_OBJECT, "resampler": ID, "color_conversion": ID, "output_width": POSITIVE,
    "output_height": POSITIVE, "output_sar": RATIONAL})
PROFILE = obj({"id": ID, "version": ID, "evidence": EVIDENCE, "receipts": array(TEXT), "fps": RATIONAL,
    "lattice": obj({"offset": COUNT, "step": POSITIVE}), "shape_min": POSITIVE,
    "policy_inference_min": POSITIVE, "policy_inference_max": POSITIVE, "policy_duration_max": RATIONAL,
    "grid": POSITIVE, "base_family": enum("ref2va", "fl2va"), "components": mapping(JSON_OBJECT),
    "node_signatures": mapping(DIGEST), "core_revision": ID, "runtime": JSON_OBJECT,
    "sampling": JSON_OBJECT, "control_branch": JSON_OBJECT, "memory_policy": ID})
AUDIO = obj({"mode": enum("preserve", "generate", "mute"), "source_media_id": nullable(ID),
    "source_offset": RATIONAL, "sample_rate": POSITIVE, "channel_layout": ID,
    "decisions": array(obj({"segment_id": ID, "mode": enum("preserve", "generate", "mute")})),
    "rounding": {"const": "absolute_half_up"}, "sample_count": COUNT, "codec": JSON_OBJECT,
    "presentation": JSON_OBJECT})
NORMALIZATION = obj({"version": ID, "t0": RATIONAL, "duration": RATIONAL, "rounded_frame_count": COUNT,
    "frame_count": POSITIVE, "duration_error": RATIONAL,
    "duration_clamp": obj({"applied": BOOL, "reason": enum(None, "minimum_one_frame"),
        "before_frame_count": COUNT, "after_frame_count": POSITIVE}), "pts_digest": DIGEST,
    "report": JSON_OBJECT})
COMMON = {"id": ID, "count": COUNT, "positive": POSITIVE, "range": RANGE, "rational": RATIONAL,
    "digest": DIGEST, "locator": LOCATOR, "error": ERROR, "settings": SETTINGS, "overrides": OVERRIDES,
    "media_ref": MEDIA, "spatial_transform": SPATIAL, "render_profile": PROFILE, "audio_timeline": AUDIO}


def standalone(name, fields, optional=()):
    return obj({"kind": {"const": "kmin." + name},
                "schema_version": {"type": "string", "pattern": r"^2\.[0-9]+\.[0-9]+(?![\s\S])"}, "id": ID,
                "required_features": IDS, "extensions": EXTENSIONS, **fields},
               optional=("required_features", "extensions", *optional))


BODIES = {
"common": {"$defs": COMMON},
"settings": SETTINGS,
"media_ref": MEDIA,
"spatial_transform": SPATIAL,
"render_profile": PROFILE,
"audio_timeline": AUDIO,
"control_spec": standalone("control_spec", {
    "type": enum("off", "canny", "depth", "pose", "gray", "canny_depth", "depth_pose"), "enabled": BOOL,
    "backend": obj({"id": ID, "version": ID, "parameters": JSON_OBJECT,
        "model_digest": nullable(DIGEST), "temporal_policy": ID}),
    "strength": UNIT, "schedule": obj({"start_percent": UNIT, "end_percent": UNIT}),
    "conditioning_role": {"const": "structural_control_video"},
    "compatibility": obj({"profile_ids": IDS, "evidence": EVIDENCE,
        "checkpoint_family": ID, "checkpoint_revision": ID, "branch_block_count": POSITIVE,
        "injection_layers": array(COUNT), "adaln": ID, "grid": POSITIVE, "lattice": JSON_OBJECT,
        "input_channels": POSITIVE, "normalization_mode": ID},
        optional=("checkpoint_family", "checkpoint_revision", "branch_block_count", "injection_layers",
                  "adaln", "grid", "lattice", "input_channels", "normalization_mode")),
    "preprocess_version": ID, "map_fingerprint": nullable(DIGEST), "components": IDS,
    "representation_id": ID}, optional=("map_fingerprint", "components", "representation_id")),
"segment": standalone("segment", {
    "revision": POSITIVE, "project_id": ID, "useful_range": RANGE, "source_media_id": ID,
    "source_range": RANGE, "boundary_before": enum("first", "cut", "continue"), "continuity_group_id": ID,
    "overrides": OVERRIDES, "analysis_ids": IDS, "prompt_draft_ids": IDS,
    "resolved_settings_digest": DIGEST, "selected": BOOL, "passthrough": BOOL},
    optional=("resolved_settings_digest",)),
"generation_window": standalone("generation_window", {
    "project_id": ID, "segment_id": ID, "plan_revision": POSITIVE, "ordinal": COUNT,
    "useful_range": RANGE, "inference_frame_count": POSITIVE, "output_useful_range": RANGE,
    "input_spans": array({"oneOf": [
        obj({"role": {"const": "useful"}, "inference_range": RANGE, "media_id": ID, "source_range": RANGE}),
        obj({"role": {"const": "padding"}, "inference_range": RANGE, "repeat_frame": COUNT}),
        obj({"role": {"const": "context"}, "inference_range": RANGE,
             "continuation_state_id": ID, "tail_map_id": ID, "source_range": RANGE})]}, minItems=1),
    "context": obj({"mode": enum("none", "structural_source", "previous_generated"), "before": COUNT,
        "after": COUNT, "dependency_result_ids": IDS, "continuation_state_id": nullable(ID)}),
    "padding": obj({"before": COUNT, "after": COUNT, "method": {"const": "repeat_boundary"}}),
    "spatial_transform_id": ID, "control_spec_id": ID, "render_profile_id": ID,
    "resolved_settings": SETTINGS, "resolved_settings_digest": DIGEST, "plan_digest": DIGEST,
    "generation_key": DIGEST, "compiled_prompt": TEXT, "prompt_recipe_id": nullable(ID),
    "reference_manifest": array(SOCKET)}),
"render_result": standalone("render_result", {
    "request_id": ID, "attempt": POSITIVE, "project_id": ID, "segment_id": nullable(ID), "window_id": nullable(ID),
    "generation_key": DIGEST,
    "status": enum("planned", "queued", "running", "succeeded", "failed", "cancelled", "blocked", "stale", "passthrough"),
    "stage": enum("prepare", "control", "sample", "decode", "trim", "export"),
    "progress": obj({"done": COUNT, "total": COUNT, "unit": ID}), "artifacts": array(MEDIA),
    "coverage": nullable(obj({"useful_range": RANGE, "output_useful_range": RANGE,
        "requested_frames": POSITIVE, "decoded_frames": POSITIVE, "useful_frames": POSITIVE,
        "width": POSITIVE, "height": POSITIVE, "fps": RATIONAL,
        "padding_removed": BOOL, "context_removed": BOOL, "pts_digest": DIGEST})),
    "audio": nullable(JSON_OBJECT), "provenance": JSON_OBJECT,
    "validation": obj({"evidence_kind": enum("real_gpu", "cpu_media", "mock"),
                       "gpu": enum("not_performed", "passed", "failed"), "receipts": array(TEXT)}),
    "error": nullable(ERROR), "warnings": array(TEXT)}),
"detection_proposal": standalone("detection_proposal", {
    "project_id": ID, "canonical_media_id": ID, "source_digest": DIGEST, "boundary_frame": COUNT,
    "detector": obj({"id": ID, "version": ID, "parameters": JSON_OBJECT}), "score": NUMBER,
    "score_scale": TEXT, "evidence_media_ids": IDS, "state": enum("proposed", "accepted", "rejected", "adjusted"),
    "accepted_boundary": nullable(COUNT), "decision_revision": COUNT}),
"scene_analysis": standalone("scene_analysis", {
    "project_id": ID, "segment_id": ID, "segment_revision": POSITIVE, "source_digest": DIGEST,
    "analyzer": PIN, "sampling_recipe": JSON_OBJECT,
    "chunks": array(obj({"range": RANGE, "sample_ids": IDS, "max_sample_gap": COUNT, "summary": TEXT})),
    "samples": array(obj({"id": ID, "media_id": ID, "frame": COUNT, "time": RATIONAL,
                          "digest": DIGEST, "duplicate": BOOL})),
    "unobserved_intervals": array(RANGE), "max_sample_gap": COUNT,
    "observations": array(obj({"category": enum("subject", "action", "camera", "environment", "source_style"),
                               "text": TEXT, "event_range": nullable(RANGE), "uncertainty": TEXT})),
    "no_inferred_transcript": {"const": True}, "transcript_id": nullable(ID), "draft_revision": COUNT,
    "errors": array(ERROR), "warnings": array(TEXT)}),
"prompt_recipe": standalone("prompt_recipe", {
    "project_id": ID, "segment_id": ID, "revision": POSITIVE, "segment_revision": POSITIVE,
    "status": enum("draft", "accepted", "superseded"), "authored_intent": TEXT,
    "dialogue_locks": array(TEXT), "visible_text_locks": array(TEXT), "analysis_ids": IDS,
    "desired_style": TEXT, "format_id": enum("h3.base/1", "h3.ref/1"), "format_version": ID, "guide": PIN,
    "mode": enum("t2va", "i2va", "fl2va", "l2va", "ref2va"), "blocks": mapping(TEXT),
    "final_text": TEXT, "text_digest": DIGEST,
    "event_ranges": array(obj({"range": RANGE, "text": TEXT})), "reference_binding_ids": IDS,
    "validation": JSON_OBJECT, "accepted": nullable(obj({"text": TEXT, "revision": POSITIVE, "digest": DIGEST})),
    "enhancer": nullable(PIN), "warnings": array(TEXT)}),
"reference_binding": standalone("reference_binding", {
    "project_id": ID, "subject_id": ID, "image_media_id": ID, "content_digest": DIGEST,
    "role": enum("identity", "appearance", "costume", "object", "style"), "segment_ids": IDS,
    "useful_ranges": array(RANGE), "appearance_state_id": ID, "description": TEXT,
    "approved": BOOL, "revision": POSITIVE, "retention_instructions": TEXT}),
"continuation_state": standalone("continuation_state", {
    "project_id": ID, "segment_id": ID, "window_id": ID, "continuity_group_id": ID,
    "predecessor_result_id": ID, "predecessor_digest": DIGEST, "profile_id": ID,
    "component_signatures": JSON_OBJECT, "geometry": JSON_OBJECT, "latent_signatures": JSON_OBJECT,
    "artifacts": array(MEDIA), "last_useful_global_end": POSITIVE, "last_useful_local_end": POSITIVE,
    "video_tail_range": RANGE, "audio_tail_range": nullable(RANGE), "mapping_recipe": ID,
    "overlap_frames": enum(5, 22, 39, 56), "audio_correction": JSON_OBJECT,
    "validity": enum("unverified", "valid", "stale", "incompatible"), "evidence": EVIDENCE,
    "generation_key": DIGEST, "revision": POSITIVE}),
}
BODIES["project"] = standalone("project", {
    "revision": POSITIVE, "fps": {"const": {"num": 24, "den": 1}}, "frame_count": POSITIVE,
    "source_media_id": ID, "canonical_media_id": ID, "normalization": NORMALIZATION,
    "media": mapping(MEDIA), "defaults": SETTINGS, "controls": mapping(record_ref("control_spec")),
    "render_profiles": mapping(PROFILE), "segments": array(record_ref("segment"), minItems=1),
    "audio_timeline": AUDIO, "results": mapping(record_ref("render_result")), "active_result_by_window": mapping(ID),
    "mode_drafts": JSON_OBJECT, "detection_proposals": mapping(record_ref("detection_proposal")),
    "scene_analyses": mapping(record_ref("scene_analysis")), "prompt_recipes": mapping(record_ref("prompt_recipe")),
    "subjects": mapping(obj({"id": ID, "label": TEXT})), "reference_bindings": mapping(record_ref("reference_binding")),
    "continuation_states": mapping(record_ref("continuation_state")),
    "windows": mapping(record_ref("generation_window")), "spatial_transforms": mapping(SPATIAL)},
    optional=("windows", "spatial_transforms"))
SCHEMAS = {name: {"$schema": DRAFT, "$id": BASE + name + ".schema.json", **body}
           for name, body in BODIES.items()}
