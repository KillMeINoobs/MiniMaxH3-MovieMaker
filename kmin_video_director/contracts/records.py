"""Immutable validated record values. to_dict returns a fresh editable copy."""
import json
from dataclasses import dataclass
from typing import ClassVar

from .serialization import canonical_bytes
from .validation import validate_record


@dataclass(frozen=True, init=False)
class Record:
    schema_name: ClassVar[str]
    _bytes: bytes

    def __init__(self, data):
        validate_record(self.schema_name, data)
        object.__setattr__(self, "_bytes", canonical_bytes(data))

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    def to_dict(self):
        return json.loads(self._bytes)

    def __getitem__(self, key):
        return self.to_dict()[key]

    @property
    def id(self):
        return self["id"]


class Project(Record):
    schema_name = "project"


class Segment(Record):
    schema_name = "segment"


class GenerationWindow(Record):
    schema_name = "generation_window"


class ControlSpec(Record):
    schema_name = "control_spec"


class RenderResult(Record):
    schema_name = "render_result"


class DetectionProposal(Record):
    schema_name = "detection_proposal"


class SceneAnalysis(Record):
    schema_name = "scene_analysis"


class PromptRecipe(Record):
    schema_name = "prompt_recipe"


class ReferenceBinding(Record):
    schema_name = "reference_binding"


class ContinuationState(Record):
    schema_name = "continuation_state"


class MediaRef(Record):
    schema_name = "media_ref"


class Settings(Record):
    schema_name = "settings"


class SpatialTransform(Record):
    schema_name = "spatial_transform"


class RenderProfile(Record):
    schema_name = "render_profile"


class AudioTimeline(Record):
    schema_name = "audio_timeline"


RECORD_TYPES = {c.schema_name: c for c in (Project, Segment, GenerationWindow, ControlSpec,
    RenderResult, DetectionProposal, SceneAnalysis, PromptRecipe, ReferenceBinding, ContinuationState)}
