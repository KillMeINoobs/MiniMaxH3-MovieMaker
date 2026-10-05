# KVD-WORKER/2.0.0 implementation handoff

This file documents actual imports, types and signatures. The foundation owns
shared files; consumers use the exact pushed, separately checked interface base
assigned through AO. Full CF is unaccepted. After read-only preflight, the
coordinator released M1-02 CPU-only implementation from source-reviewed ac335,
and subsequently released M1-03 CPU-only source work. Each owner uses its
assigned exact checked common base, with no shared-runtime/browser allocation.
Those exceptions do not accept UI/CF or integrate downstream code. Media/adapter code
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
paths, URIs, traversal, reserved Windows names and ambiguous separators. Select
an existing local folder with ordinary regular files and a stable folder layout
during operations. Resolution checks that the current path remains inside that
folder, including a stable link that would otherwise escape it. This is the
[M1 local storage contract](decisions/M1_LOCAL_STORAGE_SCOPE.md), not an OS
security boundary against another process changing filesystem objects during I/O.
No directory-handle/native filesystem isolation layer is used.

Standard Python operations stage and flush the complete JSON in the destination
folder. New-file publication uses an atomic no-clobber link; explicit overwrite
uses atomic replacement. A filesystem must support the required operation or
the save returns a typed error without writing a partial destination. Overwrite
requires the same Project ID and a current revision; changed edits advance it.
Staging precedes revision comparison under the same cooperative publication
lease, so API writers cannot replace a successfully saved newer revision with an
older one. `PROJECT_BUSY` is retryable. The empty `.kvd-save.lock` remains in the
save folder; the OS releases the lease on process exit. Do not unlink an active
lease. Unrelated editors do not participate in this revision protocol.

Publication is the commit point. Ordinary failures before it preserve the old
bytes and clean the temporary file when filesystem access permits. A cleanup
error after publication logs a path-redacted warning and returns the committed
save, avoiding a false failure after replacement. Readers check regular-file
type before opening. Root/locator resolution, including cycles, uses shared
typed errors with path-bearing exception context suppressed. Migration preserves
its source. `resolve_locator` returns a checked Path for this stable layout; it
does not reserve a path for later external use. Windows normal-use receipts are
recorded; POSIX runtime/FIFO verification remains NOT PERFORMED in this session.

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

The [all-nine call examples](../tests/contracts/worker_examples.py) construct
validated records and typed runtime envelopes for every protocol. The
[conformance test](../tests/imports/test_worker_conformance.py) binds each
example to its actual signature and checks argument types without invoking an
operation or assuming which handlers are registered. Separate cases verify all
nine unsupported errors against an explicitly empty registry and construct a
synthetic extension with guard handlers to prove call-shape independence. Synthetic
links, opaque unmaterialized values and planned results describe a boundary;
they are not an executable graph, decoded tensor or successful export.

```python
import inspect
from pathlib import Path
from kmin_video_director.contracts.worker import OPERATION_TYPES
from tests.contracts.worker_examples import operation_inputs

for name, arguments in operation_inputs(Path(".")).items():
    inspect.signature(OPERATION_TYPES[name].__call__).bind(None, **arguments)
    # Signature binding only: no operation is invoked.
```

`NormalizeMedia.recipe` and `AssembleExport.export_policy` are owner-versioned
`JsonObject` inputs. Their synthetic example keys do not define a decoder or
export algorithm; the downstream owner publishes its checked recipe/policy.
`ResolvedProject.settings` is `Mapping[str, Settings]`; `origins` is
`Mapping[str, Mapping[str, str]]`. `CancellationFlag.cancel()` and `check()`
provide a concrete thread-safe token; a consumer may adapt native interruption
through the `CancellationToken` protocol.

## Owned node and frontend extension mechanism

Add import-safe modules under `kmin_video_director/nodes/<owner>/`, with empty,
import-safe `__init__.py` files. Modules ending in `_nodes.py` are discovered
lexically by `kmin_video_director.registration.build_registry()`. Discovery
imports owned child packages explicitly; a broken package cannot silently
vanish. ImportError becomes `EXTENSION_IMPORT_ERROR` with the module name;
optional backend handling belongs inside an explicitly requested operation.

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

The shared import test requires the four foundation IDs as a subset and calls
`INPUT_TYPES()` on every discovered owned class with optional packages blocked.
Synthetic extension cases accept an import-safe added node, reject eager
optional imports at module/metadata stages, and retain the missing-foundation-ID
guard. Discovery, duplicate and broken-owned-package checks remain separate.

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

The human-restarted, source-approved `20541f938306ff6bbf80c01565fd318ea3bcbd82`
snapshot registered all four classes. Source/CPU-reviewed
`ac335b87c966b3353c5115c663d4344ff08c01a0` was subsequently deployed from its
exact archive; its unchanged backend and four-class catalog were verified.
Ordinary selector interaction saved RU and restored effective EN with server
readback. Complete layout/native graph roundtrip acceptance remains blocked.

The opt-in checker waits for the public initial `afterLoadGraph` hook and checks
`app.isGraphReady` and canvas availability. Each requested load records its
actual return type/value, readiness, rejection/stack and ordered native hooks:
`beforeLoadGraph`, `beforeConfigureGraph`, `afterConfigureGraph`, `afterLoadGraph`.
The configured input must match that request, including a fresh transient ID
in only the synthetic fixture's owned metadata. Configuration/completion must
retain that ID; stale events/data reject. Reserved IDs from saved input are
stripped before a fresh internal ID is assigned. All-outcome cleanup removes
only the matching current ID; serialized output/cache is marker-free, with
other metadata and custom titles preserved. A fulfilled undefined result from
a return-discarding wrapper requires the complete per-call sequence plus exact
serialized fixture data, four owned panels, two links and a usable canvas.
True also requires those assertions; false, rejected, unrelated, incomplete,
duplicated or out-of-order loads fail. Graph/canvas/panels are checked after
every load and again before acceptance. A caught load failure or missing final
panel cannot count as PASS. These APIs are declared
by the checked frontend's
[v1.53.6 extension interface](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/types/comfy.ts)
and [application API](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/scripts/app.ts).
The deferred callback avoids recursively awaiting the loader from its own hook;
elapsed time is not the readiness condition. Only the explicit opt-in synthetic
fixture is loaded, with asset scans skipped and no queue call. Failed checks
attempt to restore the original KVD preference, reporting success only after
verified persistence. Each requested asynchronous native load has a 15-second
failure deadline; failure restoration and final preference readback each have
their own 15-second deadline. Expiry invalidates acceptance and records pending
return state. It cannot establish readiness or cancel native work. Browser
timers cannot preempt a synchronously blocked event loop. Late settlements are
handled and logged as unaccepted; they cannot retry, save a fixture, revive PASS
or remove a newer request's marker. Only a successful opted-in check exposes its
synthetic native serialized workflow in the console receipt.

The [exact-daf review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5414488723)
requested F15/F16 changes after its 29 frontend tests passed. The coherent owner
correction has 36 frontend checks and 29 focused shared import/conformance
checks passing. These results require a new pinned review before deployment and
actual browser acceptance. The installed ac335 checker remains unchanged.
See the [validation receipt](validation/M1_FOUNDATION.md).

The subsequent c923 source/synthetic review approved those bounded checker and
shared-test corrections. Its exact archive was deployed without backend changes.
The one authorized live roundtrip rejected a stable serialization mismatch;
ordered native completion and a fulfilled `undefined` did not override that
rejection. The captured Project JSON value stayed unchanged across EN/RU/EN,
but the failed stable projection was absent. Neither a differing field nor its
cause is established. Registration and ordinary selector readback/restoration
are separate from unaccepted graph/layout/save-reload/CF evidence.

The local follow-up retains the same exact stable JSON comparison. A differing
comparison now records `semantic_failure` in the opt-in console receipt before
throwing: stage/load ID, complete expected/actual stable projections, and the
deterministic first bracket-form JSON path with values, JSON types and presence.
Missing object fields and array indices are distinct from explicit null; array
and object-key order remain significant. Cosmetic data stays outside the
existing projection, and custom titles keep their separate checks.

Diagnostics are limited to 262,144 JavaScript string code units including their
JSON envelope. Budget/capture failure reports `status: "unavailable"` and a
capture error, with no claimed partial projection or first difference. Error
formatting is guarded; its text is limited to 1,024 code units with explicit
truncation status. The complete unavailable envelope is also budget-checked;
unavailable metadata falls back to a small fixed receipt. Neither formatting
failure nor an overlong diagnostic error can replace the original mismatch. The
original complete-string equality and error still decide rejection; deadlines,
late-settlement invalidation, verified language recovery and matching-ID cleanup
are unchanged. Native/serialization errors before a completed comparison retain
their original error without claiming captured fields. This local candidate
needs its own pinned review. No new publication, deployment or live retry has
occurred, and its synthetic diagnostics are not the missing live evidence.

The owned [language settings helper](../web/common/language-settings.js) is
shared by the real selector and checker. `SETTING_ID` remains `KVD.Language`.
`readPersistedLanguage(api)` returns `Promise<"en" | "ru" | null>` from a
status-checked native `api.fetchApi` read of only that preference.
`persistLanguage(settings, api, locale)` awaits `setSettingValueAsync`, verifies
server readback and cached locale, and returns the observed stored value.
`effectiveLanguage(null)` is the declared English default; null is still
reported separately from an explicitly stored English value. The native void
setter is unsuitable for save/restoration evidence. Its async/store/API behavior
is pinned in [settings](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/scripts/ui/settings.ts),
[store](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/platform/settings/settingStore.ts)
and [API](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/scripts/api.ts).
An HTTP-error or fulfilled write without matching readback cannot imply a save.
The selector shows localized pending/error state, current versus observed saved
language, and whether recovery was confirmed. It retains a failed save error
even when restoring the old preference succeeds. Other preferences, port keys,
values, custom titles and foreign-node presentation remain untouched.

## Version, migration and unsupported features

Schemas exported under `schemas/*.schema.json` are generated from bundled
`contracts/specs.py`; run `python tools/export_schemas.py`. An independent
Draft2020-12 validator checks them in the CPU suite. Semantic relations such as
range ordering, exact coverage, rational reduction, u64 seed bound and ID/hash
closure additionally require the Python validator. Schema-only validation does
not prove those relations.

Only schema-declared shared values receive shared semantic rules. Owner reports,
recipes, mode drafts and namespaced extensions are opaque finite JSON; a key
called `seed` or a shape called `start/end` there does not become a shared field.
Canonical seed/digest/ID/version patterns require the complete string, including
rejection of a final newline. Const/enum equality keeps JSON booleans separate
from numbers. Active results close over existing windows, scene IDs, generation
keys, exact global/local coverage and output geometry. Useful input spans link
to canonical media. Frozen window settings must match current effective scene
settings and their selected control/profile compatibility. Inactive historical
attempts may retain old generation keys; they cannot be selected as current.

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
validation. Downstream owners register real operations separately and dispatch
through `REGISTRY.require_operation`. The foundation-only `operation` guard
always rejects execution; it does not discover downstream registered handlers.

`make_id(kind)` uses UUIDs. `stable_id(kind, *identity)` hashes stable semantic
coordinates. `cache_key(layer, dependencies, *, algorithm_version)` requires
explicit content/version dependencies and rejects locator/mtime-based identity.
`cache_locator(layer, key, *, suffix="json")` yields
`cache/<layer>/2/<first-two-hex>/<digest>.<suffix>`. Layers: temporal, spatial,
control, generation, analysis, prompt, continuation, assembly. No wildcard cache
deletion or assumed downstream algorithm is implemented.
