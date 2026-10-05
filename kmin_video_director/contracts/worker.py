"""KVD-WORKER/2.0.0: callable contracts, not runtime implementations.

No media, control or rendering handler is registered by this module.
Native tensors/links remain runtime-only and never enter Project JSON.
"""
from dataclasses import dataclass, field
from pathlib import Path
from threading import Event
from typing import Mapping, Protocol, Sequence

from ..errors import fail
from .records import (AudioTimeline, ControlSpec, GenerationWindow, MediaRef, Project, RenderProfile,
                      RenderResult, Settings, SpatialTransform)
from .project_io import ResolvedProject
from .specs import COUNT, DIGEST, LOCATOR
from .validation import validate_schema, validate_locator

JsonObject = Mapping[str, object]


class CancellationToken(Protocol):
    def check(self) -> None:
        """Raise shared CANCELLED or native interruption at bounded checkpoints."""
        ...


class CancellationFlag:
    def __init__(self):
        self._event = Event()

    def cancel(self) -> None:
        self._event.set()

    def check(self) -> None:
        if self._event.is_set():
            fail("CANCELLED", "Operation was cancelled.", stage="operation")


@dataclass(frozen=True)
class OperationContext:
    asset_root: Path
    cancellation: CancellationToken
    versions: Mapping[str, str]
    # Local authorization/root/cancellation are runtime-only, never serialized.


@dataclass(frozen=True)
class ProjectLocator:
    path: str
    scheme: str = "project_relative"

    def __post_init__(self):
        validate_schema({"scheme": self.scheme, "path": self.path}, LOCATOR)
        validate_locator(self.path)


@dataclass(frozen=True)
class StreamSelection:
    video: int = 0
    audio: int | None = None

    def __post_init__(self):
        validate_schema(self.video, COUNT)
        if self.audio is not None:
            validate_schema(self.audio, COUNT)


@dataclass(frozen=True)
class ProbeOutput:
    media: MediaRef
    timing: JsonObject


@dataclass(frozen=True)
class NormalizedOutput:
    media: MediaRef
    normalization: JsonObject
    audio_timeline: AudioTimeline


@dataclass(frozen=True)
class WindowPlan:
    windows: tuple[GenerationWindow, ...]
    coverage: JsonObject


@dataclass(frozen=True)
class PreparedArtifact:
    window_id: str
    media: MediaRef
    spatial: SpatialTransform
    frame_count: int
    # Disk manifest; the media owner materializes one bounded tensor lazily.


@dataclass(frozen=True)
class ControlArtifact:
    window_id: str
    control_spec_id: str
    media: MediaRef | None  # None is the explicit control-off path.
    spatial_transform_id: str
    frame_count: int
    preview_media: MediaRef | None = None


@dataclass(frozen=True)
class CompiledPrompt:
    text: str
    digest: JsonObject
    reference_manifest: tuple[JsonObject, ...]
    timing: JsonObject


@dataclass(frozen=True)
class NativeLink:
    node_id: str
    output_index: int

    def __post_init__(self):
        if not self.node_id or type(self.node_id) is not str:
            fail("INVALID_RECORD", "Native links need a node ID.")
        validate_schema(self.output_index, COUNT)

    def as_list(self):
        return [self.node_id, self.output_index]


@dataclass(frozen=True)
class NativeModelLinks:
    model: NativeLink
    clip: NativeLink
    video_vae: NativeLink
    audio_vae: NativeLink
    patch: NativeLink | None = None


@dataclass(frozen=True)
class ExpandedRender:
    graph: Mapping[str, JsonObject]
    images: NativeLink
    audio: NativeLink | None
    order_token: NativeLink
    graph_digest: JsonObject


@dataclass(frozen=True)
class DecodedAV:
    images: object  # Native IMAGE, owned by the adapter; no torch import here.
    audio: object | None
    frame_count: int
    width: int
    height: int


@dataclass(frozen=True)
class FinalizedWindow:
    result: RenderResult
    order_token: object


@dataclass(frozen=True)
class ExportOutput:
    result: RenderResult
    report: JsonObject


class ProbeMedia(Protocol):
    def __call__(self, locator: ProjectLocator, selection: StreamSelection, *, context: OperationContext) -> ProbeOutput: ...


class NormalizeMedia(Protocol):
    def __call__(self, media: MediaRef, recipe: JsonObject, *, context: OperationContext) -> NormalizedOutput: ...


class PlanWindows(Protocol):
    def __call__(self, snapshot: ResolvedProject, profile: RenderProfile, *, context: OperationContext) -> WindowPlan: ...


class PrepareWindow(Protocol):
    def __call__(self, window: GenerationWindow, canonical_media: MediaRef, spatial: SpatialTransform,
                 *, context: OperationContext) -> PreparedArtifact: ...


class BuildControl(Protocol):
    def __call__(self, prepared: PreparedArtifact, control: ControlSpec, *, context: OperationContext) -> ControlArtifact: ...


class CompileWindowPrompt(Protocol):
    def __call__(self, window: GenerationWindow, settings: Settings, bindings: Sequence[JsonObject],
                 *, context: OperationContext) -> CompiledPrompt: ...


class ExpandNativeRender(Protocol):
    def __call__(self, window: GenerationWindow, profile: RenderProfile, models: NativeModelLinks,
                 control: ControlArtifact, prompt: CompiledPrompt, order_token: NativeLink | None,
                 *, context: OperationContext) -> ExpandedRender: ...


class FinalizeWindow(Protocol):
    def __call__(self, decoded: DecodedAV, window: GenerationWindow, snapshot: ResolvedProject,
                 spatial: SpatialTransform, attempt: int, request_id: str, order_token: object,
                 *, context: OperationContext) -> FinalizedWindow: ...


class AssembleExport(Protocol):
    def __call__(self, project: Project, results: Sequence[RenderResult], audio: AudioTimeline,
                 export_policy: JsonObject, *, context: OperationContext) -> ExportOutput: ...


OPERATION_TYPES = {c.__name__: c for c in (ProbeMedia, NormalizeMedia, PlanWindows, PrepareWindow, BuildControl,
    CompileWindowPrompt, ExpandNativeRender, FinalizeWindow, AssembleExport)}
