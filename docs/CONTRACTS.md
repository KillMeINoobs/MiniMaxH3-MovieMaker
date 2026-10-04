# Proposed contracts 1.0.0

**Proposal only: no schemas, classes, nodes, interfaces or tests are implemented.** Worker interface family: `KVD-WORKER/1.0.0`; serialized record family: `kmin.*`, `schema_version: "1.0.0"`. One foundation owner turns this document into a checked implementation before downstream work. [Research](RESEARCH.md) separates source capabilities from these product policies; [architecture](ARCHITECTURE.md) assigns responsibilities.

## Types and compatibility

| Type | Definition |
|---|---|
| `Id` | Stable opaque UTF-8 string, 1–96 characters, unique within its kind. Production creation uses UUIDs with a kind prefix; short demo IDs below are illustrative. Never use array index/display label as identity. |
| `FrameIndex` / `FrameCount` | Nonnegative safe JSON integer; count may be zero only for empty optional streams, not a useful segment/window. |
| `FrameRange` | `{start: FrameIndex, end: FrameIndex}`, half-open, `start<end`. Coordinate space must be named by its enclosing field. |
| `Rational` | `{num: integer, den: positive integer}`, reduced. Time calculations use integer rational arithmetic, not repeated floating addition. |
| `Digest` | `{algorithm:"sha256", hex:string}` with exactly 64 lowercase hex characters. Placeholder all-zero examples below are not measured fingerprints. |
| `MediaId` / `ResultId` | `Id` referencing an existing media/result manifest entry. A path string is not identity. |
| `Settings` | Complete resolved `{prompt, seed, control_spec_id, audio_mode, reference_ids, spatial_policy, render_profile_id}`. Prompt is authored visible text; seed is an integer 0..2^64−1 serialized as a decimal string. |
| `Override<T>` | Absent field=inherited; present value=replaces that whole field. Null allowed only for declared nullable types; `[]` explicitly clears references. No undocumented recursive merge. |
| `Status` | `planned`, `queued`, `running`, `succeeded`, `failed`, `cancelled`, `blocked`, `stale`, `passthrough`. Success requires durable validated output. |

Every standalone Project, Segment, GenerationWindow, ControlSpec and RenderResult has `kind`, `schema_version` and `id`. Nested shared records are interpreted under the enclosing schema version. Interface and data version need not advance together; provenance records both.

Major change: reject unknown major with `UNSUPPORTED_SCHEMA_MAJOR`; preserve the original file and offer an explicit migration, never coerce or downgrade. Minor changes may add optional fields with defined defaults; reject unknown required features/enums, preserve unknown optional extensions in a namespaced `extensions` object on round trip. Patch changes do not change meanings. A future migrator is explicit, deterministic, writes a new file, records from/to version and checksums, retains IDs when semantics permit, and marks affected plans/results stale. No migration code exists in M0.

## MediaRef and source time

Project contains a `media` map keyed by MediaId. Each MediaRef has:

| Field | Type / invariant |
|---|---|
| `id`, `role` | Id; `source_video`, `reference_image`, `reference_video`, `reference_audio`, `prepared_video`, `control_map`, `render_video`, `audio_pcm` |
| `locator` | `{scheme:"project_relative"|"local_absolute", path:string}`. Unicode/spaces preserved. Resolve explicitly within approved roots; no URL download or relink-by-filename search. Absolute locators are local-only and redacted from public provenance. |
| `fingerprint` | Content Digest plus byte_size integer, mtime_ns decimal string (fast hint only), selected stream indices and probe/decoder version. Recheck content before reuse; equal size/mtime alone does not prove identity. |
| `probe` | Codec/stream IDs, stream time_bases, decoded video PTS-index digest, first PTS, final-frame endpoint, rational rates, VFR flag, coded dimensions, display matrix/rotation, SAR, color/pixel format; selected audio rate/channels/start PTS/skip-samples metadata or `audio:null`. |
| `availability` | `available` or `missing`/`changed` with structured error; inaccessible source is not replaced by a guessed file. |

Canonical origin is the selected video's first displayed decoded PTS `t0`. Source timestamps remain in the manifest; audio offset is `audio_first_effective_pts - t0`, not independently zeroed. A missing final frame duration/timestamp produces `AMBIGUOUS_MEDIA_TIMING` until an explicit documented policy resolves it. Count is not derived from nominal FPS × container duration alone.

**Proposed normalization rule:** duration `D` is the selected decoded video's presentation span; `F=max(1, round_half_up(24*D))`. Store D, F and quantization error (absolute error <=1/48 s under this rule). Produce exactly F real decoded CFR frames at PTS `j/24`, using a documented timestamp resampler (candidate FFmpeg fps nearest rounding) and explicit EOF correction to F. Log drops/duplicates and any last-frame hold; never change playback speed by reinterpreting metadata. Verify PTS and decoded count, not just average_frame_rate. Missing frames/discontinuities are errors or explicit held intervals recorded in provenance. No motion interpolation by default.

Normalize once, stream to a disk artifact and PTS manifest. Window access uses canonical frame indices; keyframe seek must decode/discard to the exact boundary. Do not independently resample each segment. Time normalization and spatial preparation have separate keys so a prompt edit does not re-decode media.

## Project

| Field | Type / invariant |
|---|---|
| `kind`, `schema_version`, `id`, `revision` | `kmin.project`, `1.0.0`, Id, monotonically increasing integer for saved edits |
| `fps`, `frame_count`, `source_media_id`, `canonical_media_id` | fps exactly `{num:24,den:1}`; measured positive F; source/canonical MediaId |
| `normalization`, `media` | Recipe/version/t0/D/F/PTS digest/drop-hold report; MediaRef map |
| `defaults`, `controls`, `render_profiles` | Settings; ControlSpec map; immutable compatibility profiles with version/evidence level |
| `segments` | Ordered Segment array covering `[0,F)` exactly once; contiguous, no unintended overlap/gap; IDs independent of order |
| `audio_timeline` | AudioTimeline below |
| `results`, `active_result_by_window` | RenderResult references; explicit chosen result per window, no latest-file heuristic |
| `mode_drafts`, `extensions` | Namespaced saved settings for deferred modes; retained while switching modes, never interpreted as supported capability |

An illustrative fragment (other fields are defined by the table, not supplied files):

```json
{
  "kind": "kmin.project", "schema_version": "1.0.0", "id": "proj-demo",
  "revision": 1, "fps": {"num": 24, "den": 1}, "frame_count": 360,
  "source_media_id": "media-source", "canonical_media_id": "media-cfr",
  "defaults": {
    "prompt": "A cinematic scene with the source motion.", "seed": "43",
    "control_spec_id": "ctrl-canny", "audio_mode": "preserve",
    "reference_ids": [], "spatial_policy": "preserve_display_pad",
    "render_profile_id": "native-union-v1-demo"
  },
  "mode_drafts": {"vid2va": {}, "ref2va": {}}, "extensions": {}
}
```

`mode_drafts` entries preserve state only; v1 MVP accepts VID2VA/Canny/off. Future unsupported modes fail capability validation while their draft settings survive.

## Segment and inheritance

| Field | Type / invariant |
|---|---|
| `kind`, `schema_version`, `id`, `revision`, `project_id` | `kmin.segment`, version, stable Id, revision integer, Project Id |
| `useful_range` | FrameRange in canonical project coordinates |
| `source_media_id`, `source_range` | Canonical MediaId; same range as useful_range for v1 unretimed source timeline |
| `boundary_before` | `cut` or `technical_split`; explicit editorial intent, no implied continuation |
| `overrides` | Partial Settings under replacement rules; field origin recorded in resolved settings |
| `resolved_settings_digest` | Digest of complete effective Settings; each window stores an immutable resolved snapshot |
| `selected`, `passthrough` | bool selection; passthrough false by default, true explicitly uses source and labels result `passthrough` |

```json
{
  "kind": "kmin.segment", "schema_version": "1.0.0", "id": "seg-demo",
  "revision": 1, "project_id": "proj-demo", "source_media_id": "media-cfr",
  "useful_range": {"start": 0, "end": 360},
  "source_range": {"start": 0, "end": 360}, "boundary_before": "cut",
  "overrides": {"prompt": "A stone dancer moves across a desert.", "reference_ids": []},
  "selected": true, "passthrough": false
}
```

Overrides never concatenate prompts or add hidden refs. Editing a marker keeps segment IDs where practical but increments revisions and replans affected windows. Selected-only generation can leave missing results; full export reports missing ranges instead of silently passing through.

## GenerationWindow and capabilities

| Field | Type / invariant |
|---|---|
| `kind`, `schema_version`, `id`, `project_id`, `segment_id`, `plan_revision`, `ordinal` | `kmin.generation_window`; stable IDs; plan revision; nonnegative ordering ordinal |
| `useful_range` | Global canonical FrameRange; windows partition their segment exactly once |
| `inference_frame_count`, `output_useful_range` | N; local decoded `[a,b)` with `b-a=useful.end-useful.start` and `0<=a<b<=N` |
| `input_spans` | Ordered list `{role, inference_range, media_id?, source_range?, repeat_frame?}`; roles `useful`, `context`, `padding`; local ranges partition `[0,N)` exactly |
| `context` | `{mode:"none"|"structural_source"|"previous_generated", before:FrameCount, after:FrameCount, dependency_result_ids:Id[]}`. v1 MVP requires none/0/0/[]; future context requires an enabled tested capability |
| `padding` | `{before:FrameCount, after:FrameCount, method:"repeat_boundary"}`; no useful frames assigned to padding |
| `spatial_transform_id`, `control_spec_id`, `render_profile_id` | Links to exact frozen recipes/profiles; resolved Settings snapshot and Digest |
| `plan_digest`, `generation_key` | Content-addressed plan/key including algorithm and adapter versions; deterministic window ID derived from project/segment/plan revision/ordinal/ranges, not an ephemeral node ID |

For the S01 native pin, capability proposal is `fps=24`, `lattice={offset:5,step:17}`, `shape_min=5`, `policy_inference_min=124`, `policy_duration_max={num:15,den:1}`, `policy_inference_max=345`, `grid=32`. Source-only evidence accompanies the profile; operational quality floor and cap are our policy. Profile changes replan; no blind future constant. Validate integer N, `(N-5)%17==0`, `124<=N<=345`, and N includes *every* useful/pad/context frame. Reject an unaligned request even if native would snap it.

Proposed planner for one segment of L useful frames without context: `m=ceil(L/345)`; distribute useful counts as evenly as possible across m windows, with earlier windows receiving the remainder; `N=smallest legal lattice count >=max(124, useful_count)`. Never rebalance across a real cut or distinct prompt boundary. This avoids tiny technical tails; intrinsically short user segments are padded explicitly. Seed per window is derived deterministically and stored, so retry is stable.

Exactly 15 seconds means F=360 useful frames. Proposed plan: two useful ranges `[0,180)`, `[180,360)`; N=192 each; 12 tail pad frames each; export 360 frames, not 384. For L=346: two 173 useful windows, N=175. For L=1000: 334/333/333 useful frames, N=345 each. For L=1: N=124, remove 123 pad frames. These are mathematical design examples, not executed tests.

```json
{
  "kind": "kmin.generation_window", "schema_version": "1.0.0", "id": "win-demo-1",
  "project_id": "proj-demo", "segment_id": "seg-demo", "plan_revision": 1, "ordinal": 0,
  "useful_range": {"start": 0, "end": 180}, "inference_frame_count": 192,
  "output_useful_range": {"start": 0, "end": 180},
  "input_spans": [
    {"role": "useful", "inference_range": {"start": 0, "end": 180},
     "media_id": "media-cfr", "source_range": {"start": 0, "end": 180}},
    {"role": "padding", "inference_range": {"start": 180, "end": 192}, "repeat_frame": 179}
  ],
  "context": {"mode": "none", "before": 0, "after": 0, "dependency_result_ids": []},
  "padding": {"before": 0, "after": 12, "method": "repeat_boundary"},
  "spatial_transform_id": "space-demo", "control_spec_id": "ctrl-canny",
  "render_profile_id": "native-union-v1-demo"
}
```

The window's prepared IMAGE batch must be exactly `[N,H,W,3]`, canvas H/W exact, numeric domain 0..1. Future before-context shifts the useful local start; trim uses `output_useful_range`, not guessed overlap. Continuation invalidates dependent windows when its result changes and cannot increase total N beyond the cap.

## SpatialTransform

Record `id`, version, coded W/H, source SAR/display matrix, displayed W/H after orientation, scale rational, fitted content W/H, canvas W/H, content rectangle `{x,y,width,height}`, pad fill by modality, resampler/color conversion and output W/H/SAR. Default `preserve_display_pad` uses displayed size, no hidden crop or downscale; pad to multiples of 32 and crop service padding after generation. Declared Draft/max-megapixels may rescale content with aspect-preserving rounding; record resulting scale and <=1-pixel fit error. No automatic lower resolution on OOM.

Illustration: square-pixel 640×360 → canvas 640×384, content rectangle `(0,12,640,360)` → output 640×360, SAR 1/1. A 90-degree coded 320×240 input displays 240×320. SAR 16/15 at coded 720×576 displays 768×576. These transformations require future checks.

RGB/control/masks/result share the same coordinates; map padding values may differ and are declared (e.g. black Canny/no-mask padding). Build Canny on fitted useful content then apply the same pad rectangle to avoid artificial edge bars. Native receives exact canvas-sized maps so its center-fit path cannot introduce a second geometric operation. Original odd display dimensions remain exact if chosen codec supports them; otherwise `UNSUPPORTED_EXPORT_DIMENSIONS` offers an explicit codec or visible pad choice. Never silently change them.

## ControlSpec and model profile

| Field | Type / invariant |
|---|---|
| `kind`, `schema_version`, `id` | `kmin.control_spec`, version, stable Id |
| `type`, `enabled` | `off`, `canny`, `depth`, `pose`, `gray`, `canny_depth`, `depth_pose`; bool. v1 capability accepts only canny/off |
| `backend` | `{id, version, parameters, model_digest:null|Digest, temporal_policy}`. Canny threshold domain/backend must be explicit; no OpenCV 0..255 vs native 0..1 confusion |
| `strength`, `schedule` | finite number; MVP 0..1 validated subset; `{start_percent,end_percent}` with `0<=start<=end<=1`, denoising schedule only |
| `conditioning_role` | Always `structural_control_video`; never implicit RGB-reference |
| `compatibility` | Allowed profile IDs, checkpoint family/revision, branch block count/injection layers, AdaLN representation, grid/lattice/input channels, normalization mode, evidence level |
| `preprocess_version`, `map_fingerprint` | Versioned pipeline and resulting map manifest digest when built |

```json
{
  "kind": "kmin.control_spec", "schema_version": "1.0.0", "id": "ctrl-canny",
  "type": "canny", "enabled": true, "conditioning_role": "structural_control_video",
  "backend": {"id": "comfy-native-canny", "version": "core-b87fe48",
              "parameters": {"low_threshold": 0.4, "high_threshold": 0.8},
              "model_digest": null, "temporal_policy": "fixed_parameters"},
  "strength": 1.0, "schedule": {"start_percent": 0.0, "end_percent": 1.0},
  "compatibility": {"profile_ids": ["native-union-v1-demo"], "evidence": "source_only"},
  "preprocess_version": "canny-pipeline/1"
}
```

Off bypasses patch application; it does not turn RGB into another conditioning path. Combined enum values reserve future formats only; reject them until tested backend/checkpoint support exists. Depth backend must record sequence-level scaling/alignment; no unexplained independent per-frame normalization.

A RenderProfile names every installed component (base family FL2VA/Ref2VA, base/patch/text/video-VAE/audio-VAE file + content digest + upstream revision/conversion), core revision and node schema signatures, dtype/quantization/kernel/attention, sampler/scheduler/steps/shifts/LoRAs, expected control branch form and memory policy. S01 loader supports shape-derived placement, but profile validation must check missing/unexpected keys and metadata, especially ten-block v2/post_norm and full vs basis AdaLN. No filename-only compatibility and no silently dropping half a branch. Profile state `source_only` → `load_verified` → `gpu_verified` requires attached receipts; M0 only establishes the first.

## AudioTimeline

Fields: `mode` default preserve; selected source audio MediaId or null; rational source offset relative to t0; output sample_rate/channel layout; ordered per-segment decisions; `rounding:"absolute_half_up"`; final sample_count; codec/mux configuration; source/decode skip_samples, encoder priming/trailing padding and mux edit-list/PTS observations. Preserve mode with no audio produces no stream plus a visible note. Mute produces no stream; optional silence is a separate explicit export choice. Generate uses H3-decoded audio, not source-audio reference conditioning.

For nonnegative global frame f and output sample rate Fs, define **Q(f)=floor((f*Fs+12)/24)**. An output interval `[a,b)` has samples `[Q(a),Q(b))`. Use these absolute boundaries rather than sum separately rounded segment durations. At Fs=48000 a frame is 2000 samples; Fs=32000 alternates integer boundary increments. Convert an original audio sample time relative to t0 into this one global PCM timeline, retaining silence for positive offset and trimming pre-origin samples for negative offset.

Preserve: decode/resample sequentially once to disk PCM, preserve timestamp gaps and source offset; splice absolute slices, encode the final soundtrack once. Do not concatenate independently AAC-encoded per-window audio. Generate: trim decoded inference audio by local useful time, resample and fit exactly into `[Q(a),Q(b))`; record any pad/trim due to audio latent quantization. No promise of seamless generated audio across independent windows. Muted windows still retain timeline duration.

Container duration alone is insufficient. Future checks decode export, apply signaled codec priming/skip/edit-list semantics, then measure first/last/each-boundary impulses against global PCM coordinates. Desired no accumulated shift: PCM splice boundaries exact, resampling rounding <=1 output sample, any residual codec presentation offset measured once and reported; effective A/V duration error <=1 frame. Unexplained accumulated offset fails acceptance.

## RenderResult, status and errors

| Field | Type / invariant |
|---|---|
| `kind`, `schema_version`, `id`, `request_id`, `attempt` | `kmin.render_result`; stable attempt ID, unique submission identity, positive attempt count; retries create new records |
| `project_id`, `segment_id`, `window_id`, `generation_key` | Exact request association and frozen key; old output never masquerades as current |
| `status`, `stage`, `progress` | Status; prepare/control/sample/decode/trim/export stage; `{done,total,unit}`; progress is not success |
| `artifacts` | MediaRef entries, checksums and paths (local-only absolute locations); partial files not active until atomic finalize |
| `coverage` | Useful global/local ranges, requested N, actual decoded N and useful count; output dimensions/fps; pad/context removed flags |
| `audio` | Mode, expected/measured samples, source offset, correction and codec presentation metadata |
| `provenance` | Resolved Settings, source/map/plan digests, full component profiles/versions, seed, expanded graph digest, prompt ID, resource owner label, timestamps, memory/time observations or null |
| `validation` | Evidence kind `real_gpu`, `cpu_media`, `mock`; GPU `not_performed`, `passed`, `failed`; receipt references. No mock/cpu_media result is GPU passed |
| `error`, `warnings` | Error or null, warning array; structured `{code,message,stage,retryable,details}` with redacted local paths in public copies |

Illustrative **unexecuted** result:

```json
{
  "kind": "kmin.render_result", "schema_version": "1.0.0", "id": "result-demo-1",
  "request_id": "request-demo", "attempt": 1, "project_id": "proj-demo",
  "segment_id": "seg-demo", "window_id": "win-demo-1", "status": "planned",
  "stage": "prepare", "progress": {"done": 0, "total": 1, "unit": "window"},
  "artifacts": [], "validation": {"evidence_kind": "mock", "gpu": "not_performed", "receipts": []},
  "error": null, "warnings": ["Illustrative record; no execution occurred."]
}
```

Transitions: planned→queued→running→succeeded/failed/cancelled; preflight may produce blocked. Editing dependencies marks a prior success stale, retaining artifacts/history. Passthrough is explicit and cannot satisfy generation acceptance. Success requires final atomic files, matching key, exact counts/dimensions/PTS and validation receipts. Interrupted work keeps validated prior windows; in-flight partial files remain inactive. Do not automatically retry an ambiguous completed submission before reconciling its request/artifact receipt.

Initial error codes include `SOURCE_MISSING`, `SOURCE_CHANGED`, `AMBIGUOUS_MEDIA_TIMING`, `UNSUPPORTED_SCHEMA_MAJOR`, `UNSUPPORTED_CAPABILITY`, `MODEL_INCOMPATIBLE`, `RESOURCE_LIMIT`, `FRAME_COUNT_MISMATCH`, `UNSUPPORTED_EXPORT_DIMENSIONS`, `AUDIO_SYNC_MISMATCH`, `CANCELLED`, `PARTIAL_RESULT`. Missing installed models block; corrupted decode/count failures fail. Targeted retry only reuses checked inputs and deterministic settings.

## Cache and invalidation

Canonical JSON hashing sorts keys, retains order of semantic arrays, forbids NaN/Infinity and hashes explicit effective defaults. Include schema/algorithm/decoder/backend/adapter versions and immutable content digests. Paths/mtime are resolution hints, not authoritative generation keys.

| Cache | Inputs to key | Changes that invalidate |
|---|---|---|
| Temporal media | Source content/selected streams/PTS, decoder and normalization policy version | Source/stream/timing/recipe change; not prompt/seed |
| Spatial prepared windows | Temporal artifact, input spans/padding, spatial/color recipe version | Transform/window/pad changes; not prompt |
| Control maps | Prepared content/transforms, Canny thresholds or backend/model/temporal calibration/version | Geometry/source/control backend/params change; not prompt/seed/denoising strength |
| Generation | Resolved prompt/seed/refs/content hashes, plan/maps, model/kernel/core signatures, schedule/strength/sampling/adapter versions | Any conditioning/model/plan change; context predecessor result digest propagates invalidation |
| Assembly | Ordered chosen result digests/useful trims/spatial inverse/audio timeline/export codec version | Result choice, audio/export policy or trim change; cached renders can remain valid |

Schema major always invalidates incompatible caches. Algorithm/profile version changes invalidate only dependent layers; no wildcard whole-cache deletion. Cache manifests are atomic and checksum-validated. Export audio_mode changes need not invalidate video inference when no conditioning/sampling changes, even though the assembled result key changes.

## Worker-facing interfaces

All names here are proposed logical interfaces, not code signatures or implemented file names. Foundation owner publishes one `KVD-WORKER/1.0.0` checked commit with serialization, error and conformance examples before media/H3 owners start.

| Interface | Input → output / obligation |
|---|---|
| `ProbeMedia` | Approved locator/stream selection → MediaRef/TimingReport; read-only, no downloads |
| `NormalizeMedia` | MediaRef/normalization recipe/cancel token → canonical disk MediaRef/PTS report; exactly F CFR frames |
| `ResolveProject` | Project → validated immutable settings/media snapshot; missing assets/capabilities explicit |
| `PlanWindows` | Snapshot/RenderProfile → ordered GenerationWindows/coverage report; pure CPU logic |
| `PrepareWindow` | Window/canonical media/spatial recipe/cancel token → bounded prepared artifact; no all-video tensor |
| `BuildControl` | Prepared artifact/ControlSpec → map manifest/preview; one declared transform, no appearance refs |
| `ExpandNativeRender` | Window/profile/model links/maps/resolved settings/order token → native graph result links; deterministic IDs, no HTTP requeue |
| `FinalizeWindow` | Native decoded AV/window/snapshot → checked RenderResult/disk artifact/order token; trims padding/context and releases owned buffers |
| `AssembleExport` | Project/ordered selected RenderResults/AudioTimeline/export policy → export RenderResult plus frame/sample/PTS report; no silent holes |
| `RunSelection` | Snapshot/selected IDs/resume ledger → owned native prompt/progress/ledger events; serial policy, reconcile before retry |

Typed operation failure returns the shared error structure; cancellation is honored between bounded operations and surfaces native interruption. CPU/media/adapter owners own their ordinary tests/docs. Shared interface changes require foundation-owner integration and a new recorded common SHA before consumers proceed.
