# KVD-WORKER/2.0.0 implementation handoff

This file documents actual imports, types and signatures. The foundation owns
shared files; consumers start only from the exact pushed, separately checked CF
assigned through AO. A symbolic CF label is insufficient. Media/adapter code
does not exist in this foundation. No callable handler for the nine downstream
operations is registered yet.

## Portable records and I/O

Import records and helpers from `kmin_video_director.contracts`:
`Project`, `Segment`, `GenerationWindow`, `ControlSpec`, `RenderResult`,
`DetectionProposal`, `SceneAnalysis`, `PromptRecipe`, `ReferenceBinding`,
`ContinuationState`, `MediaRef`, `Settings`, `SpatialTransform`, `RenderProfile`
and `AudioTimeline`. `Record.from_dict(data)` validates structure and semantic
invariants; `record.to_dict()` returns a new mutable copy. The stored canonical
UTF-8 bytes and record identity are immutable. `record[key]` reads a copied value.

```python
from kmin_video_director.contracts import (
    Project, loads, dumps, load_project, save_project, resolve_project,
    resolve_locator, cache_key, cache_locator, make_id, stable_id,
    migrate_v1_example, ContractError,
)

project = Project.from_dict(data)
snapshot = resolve_project(project)  # structural validation, no media reads
save_project(project, selected_folder, "projects/scene.kvd.json", overwrite=False)
restored = load_project(selected_folder, "projects/scene.kvd.json")
```

`resolve_project(project, *, asset_root=None, check_assets=False)` returns
`ResolvedProject(project, settings, origins, assets_checked)`; settings maps
segment IDs to immutable Settings, origins maps each field to `default` or
`segment`. Only `check_assets=True` opens the explicitly listed files for
streamed content hashes. It never decodes them, searches folders or guesses
relinks. Inaccessible/changed assets raise shared errors.

`loads(text)` reads a standalone kind-bearing record. Nested shared records
use their concrete class's `from_dict`. `dumps(record)`, `canonical_bytes(value)`,
`digest_json(value)` and `digest_bytes(bytes)` use sorted keys, preserved array
order and finite, safe JSON numbers. Seeds are canonical decimal strings in
0..2^64−1. `schema_version` belongs to data; interface version is independent.

Relative locators use `/`, preserve Unicode/spaces and reject absolute/drive/UNC
paths, URIs, traversal, reserved Windows names and ambiguous separators. Runtime
resolution additionally checks symlink containment. Save stages a complete file
and atomically activates it; new destinations cannot be clobbered. Explicit
overwrite requires the same Project ID and a current revision, with changed
edits advancing revision. Filesystems without the required atomic operation
return `PROJECT_IO_ERROR`. I/O errors omit machine paths.

## Downstream call signatures

All types below are exported by `kmin_video_director.contracts.worker`, except
record types/ResolvedProject above. Every operation is a `typing.Protocol`
with `__call__`. These are interfaces, **not implementations or executable
workflow nodes**. Failures raise `ContractError`; native cancellation adapters
may surface native interruption directly.

| Protocol | Positional arguments | Keyword-only / output |
|---|---|---|
| ProbeMedia | locator: ProjectLocator, selection: StreamSelection | context: OperationContext → ProbeOutput |
| NormalizeMedia | media: MediaRef, recipe: JsonObject | context → NormalizedOutput |
| PlanWindows | snapshot: ResolvedProject, profile: RenderProfile | context → WindowPlan |
| PrepareWindow | window: GenerationWindow, canonical_media: MediaRef, spatial: SpatialTransform | context → PreparedArtifact |
| BuildControl | prepared: PreparedArtifact, control: ControlSpec | context → ControlArtifact |
| CompileWindowPrompt | window: GenerationWindow, settings: Settings, bindings: Sequence[JsonObject] | context → CompiledPrompt |
| ExpandNativeRender | window, profile, models: NativeModelLinks, control, prompt: CompiledPrompt, order_token: NativeLink or None | context → ExpandedRender |
| FinalizeWindow | decoded: DecodedAV, window, snapshot, spatial, attempt: int, request_id: str, order_token: object | context → FinalizedWindow |
| AssembleExport | project, results: Sequence[RenderResult], audio: AudioTimeline, export_policy: JsonObject | context → ExportOutput |

`JsonObject = Mapping[str, object]` carries owner-specific algorithm reports or
recipes, not arbitrary tensors. Component pins and algorithm versions must be
explicit. Concrete dataclass fields are defined in `worker.py`:

- `OperationContext(asset_root: Path, cancellation: CancellationToken, versions: Mapping[str,str])` is runtime-only; cancellation exposes `check()`.
- `ProjectLocator(path, scheme="project_relative")` and `StreamSelection(video=0, audio=None)` validate their primitive values.
- `ProbeOutput(media, timing)`; `NormalizedOutput(media, normalization, audio_timeline)`; `WindowPlan(windows: tuple[GenerationWindow,...], coverage)`.
- `PreparedArtifact(window_id, media, spatial, frame_count)` is a disk manifest. The media owner materializes at most one bounded IMAGE tensor.
- `ControlArtifact(window_id, control_spec_id, media, spatial_transform_id, frame_count, preview_media=None)` uses `media=None` only for explicit control-off.
- `CompiledPrompt(text, digest, reference_manifest: tuple[JsonObject,...], timing)` records exact visible text and physical bindings.
- `NativeLink(node_id, output_index).as_list()` returns a native graph link. `NativeModelLinks(model, clip, video_vae, audio_vae, patch=None)` contains links, not loaded models.
- `ExpandedRender(graph, images, audio, order_token, graph_digest)` is a deterministic native expansion; no HTTP self-queueing.
- `DecodedAV(images, audio, frame_count, width, height)` is runtime-only. `FinalizedWindow(result, order_token)` and `ExportOutput(result, report)` require validated durable RenderResults.

The media/adapter owner validates operation-envelope manifests and actual media,
tensor domains, native links and durable outputs. A dataclass envelope or schema
PASS is not evidence that an operation executed. See the synthetic
[conformance records](../tests/contracts/fixtures/project.json): source fingerprints,
profiles and planned/mock results are intentionally labelled synthetic/missing.
They are not model-load or GPU receipts.

## Owned node and frontend extension mechanism

Add import-safe modules under `kmin_video_director/nodes/<owner>/`, with empty,
import-safe `__init__.py` files. Modules ending in `_nodes.py` are discovered
lexically by `kmin_video_director.registration.build_registry()`.

```python
# nodes/media/media_nodes.py (future media-owned file)
from ...contracts import Project
# Import optional decoder/model packages inside the actual operation only.
NODE_CLASS_MAPPINGS = {"KVD_ProbeMedia": ActualProbeNode}
NODE_DISPLAY_NAME_MAPPINGS = {"KVD_ProbeMedia": "KVD Probe Media"}
OPERATIONS = {"ProbeMedia": actual_probe_media}  # only when implemented
```

The example above describes an extension module; it is not supplied code or an
executable placeholder. Do not register a protocol as a handler. Node IDs start
with `KVD_`; duplicates, unknown operation names and broken imports fail
explicitly. `REGISTRY.require_operation(name)` returns the actual implementation
or raises `UNSUPPORTED_CAPABILITY`. Optional modules must remain import-safe;
missing optional backends fail when explicitly requested. No shared-file edit
is needed to add a node module.

Add owned JS files under `web/<owner>/`; ComfyUI discovers them through the root
`WEB_DIRECTORY="./web"`. Import `registerPresentation` from the relative
`common/presentation.js` module and register EN/RU `title`, `help`, `fields`
and `tooltips`, keyed by stable serialized names. Foundation's official
`nodeCreated`, `loadedGraphNode`, `afterConfigureGraph` hooks install/reapply the
scoped panel. `getLanguage`, `setLanguage`, `onLanguageChange`, `errorText` and
`statusText` are actual presentation APIs. Persist the global preference through
ComfyUI's `KVD.Language` setting; `setLanguage` alone changes presentation only.
Never translate `.name`, class IDs, values, socket types or enum semantics.
Custom node titles remain user-owned. Other packs/native UI are untouched.

Foundation owns shared translations/design tokens/settings and package files.
Consumers add their own presentation registration and tests; shared amendments
return to foundation. No dependency installation, model download or automatic
generation belongs in node import, discovery or frontend setup.

## Version, migration and unsupported features

Schemas exported under `schemas/*.schema.json` are generated from bundled
`contracts/specs.py`; run `python tools/export_schemas.py`. An independent
Draft2020-12 validator checks them in the CPU suite. Semantic relations such as
range ordering, exact coverage, rational reduction, u64 seed bound and ID/hash
closure additionally require the Python validator. Schema-only validation does
not prove those relations.

Unknown major → `UNSUPPORTED_SCHEMA_MAJOR`; unknown required features →
`UNSUPPORTED_REQUIRED_FEATURE`. Future 2.x optional data round-trips in
namespaced `extensions`; unknown root fields/enums are rejected. JSON input is
bounded to 8 MiB/96 nesting levels. There was no deployed v1. The explicit
`migrate_v1_example(root, source_path, destination_path)` supports only the
documented empty-reference, unretimed conformance shape: legacy `range` becomes
`useful_range`/`source_range`, `boundary_type` becomes `boundary_before`, relative
locators are normalized, refs become empty logical bindings, IDs persist, stale
plan/result selections are invalidated, and a checksum/profile receipt is added.
It writes a separate new file. Other legacy data is rejected for a new migration
profile; changing a version string alone is not migration.

Optional draft/analysis/binding/state records can be stored and validated.
`require_runtime_capabilities(operation=...)` truthfully rejects operations in
this foundation; initial control policy is Canny/off, authored text, empty refs
and no carry/context. It is a guard, not a substitute for installed component
validation. Downstream owners register real operations separately.

`make_id(kind)` uses UUIDs. `stable_id(kind, *identity)` hashes stable semantic
coordinates. `cache_key(layer, dependencies, *, algorithm_version)` requires
explicit content/version dependencies and rejects locator/mtime-based identity.
`cache_locator(layer, key, *, suffix="json")` yields
`cache/<layer>/2/<first-two-hex>/<digest>.<suffix>`. Layers: temporal, spatial,
control, generation, analysis, prompt, continuation, assembly. No wildcard cache
deletion or assumed downstream algorithm is implemented.
