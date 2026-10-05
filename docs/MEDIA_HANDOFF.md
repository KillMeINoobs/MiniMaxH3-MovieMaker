# M1 media implementation plan and handoff

Initial implementation `cd1b90f5e5d91d9c01d9fd5123dc7a2ab26f81b7` has direct
parent `ac335b87c966b3353c5115c663d4344ff08c01a0`, descended from accepted C0.
The M1-02-INTEGRATE-C923 release now integrates the entire exact common commit
`c923d9e4292ea40e4a3f37f2feace8fa252eecb4` through a normal merge preserving
that published media history. Its separate
[source/synthetic review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5415254811)
approved the common correction, including extension-aware shared tests.
All media implementation/tests, five signatures, eight node IDs, recipes and
export formats are unchanged by this integration. The preserved brief and
shared data/schema/worker interfaces remain unchanged. PR2 is draft/unmerged;
live foundation UI is BLOCKED and full CF remains unaccepted.

The approved design uses standard-library Python with an explicitly selected
external FFmpeg/ffprobe backend. Source frames and timestamps stream through
bounded buffers; canonical video, PCM and manifests live on disk. No inference,
model, queue, shared runtime or personal media operation is part of this work.

Implementation sequence:

1. `planning/windows.py`, `media/timing.py`, `media/geometry.py`: test rational
   quantization, profile-derived balanced windows, exact selected-scene coverage
   and declared display/fit/inverse geometry before implementing them.
2. `media/backend.py`, `media/probe.py`: implement lazy backend selection,
   regular-file/content checks, cancellation/quota monitoring and streamed decoded
   PTS manifests. Ambiguous EOF needs an explicit last-frame-duration policy.
3. `media/normalize.py`, `media/prepare.py`: normalize the complete source once,
   record the displayed-frame selection at each CFR24 time, prepare bounded
   disk windows, and retain the global PCM timeline with absolute sample boundaries.
4. `assembly/export.py`: validate explicit active successful results and actual
   hashes/counts/geometry, stream selected useful video, splice global PCM and
   perform one final encode. Missing coverage returns a typed error.
5. `nodes/media/`, `web/media/`: register only real operations/nodes through
   existing discovery and EN/RU presentation APIs; use persisted `KVD.Language`
   and stable class IDs, keys, values and port types.
6. Verify synthetic media, isolated import/schema/signature/presentation checks,
   bounded memory, owned documentation links, brief integrity and public privacy.
   Freeze one checked candidate for separate review; publish the authorized
   stacked draft against the foundation branch without deploying it.

The timestamp resampler uses displayed-frame hold at `j/24`: select the most
recent source frame whose relative PTS is at most that time. Dropped source
frames, duplicate selections, timestamp gaps and final-frame holds are explicit.
This deterministic policy preserves playback time without motion interpolation.
`F=max(1,round_half_up(24*D))`; quantization/clamp provenance remains exact.

## Implemented callable boundary

The five handlers in owned `OPERATIONS` implement the unchanged
[KVD-WORKER/2.0.0](../kmin_video_director/contracts/worker.py) call signatures.
Nodes dispatch through `REGISTRY.require_operation` (the registry builder),
rather than registering Protocols or bypassing the foundation-only unsupported
operation guard. Other generation/control operations remain unregistered.

| Operation | Implementation | Result |
| --- | --- | --- |
| ProbeMedia | [probe.py](../kmin_video_director/media/probe.py) | Fingerprinted selected streams; streamed decoded PTS index; explicit origin and EOF receipt |
| NormalizeMedia | [normalize.py](../kmin_video_director/media/normalize.py) | Whole-source FFV1 NUT CFR24; selection JSONL; global s16 PCM when requested |
| PlanWindows | [windows.py](../kmin_video_director/planning/windows.py) | Balanced native windows with exact selected useful ranges, no context/refs, unchanged editorial scenes |
| PrepareWindow | [prepare.py](../kmin_video_director/media/prepare.py) | One bounded disk artifact with grid padding and declared tail repeats |
| AssembleExport | [export.py](../kmin_video_director/assembly/export.py) | Verified explicitly selected useful outputs, exact global audio mapping and checked final encode |

All portable records use existing immutable foundation records and generated
schemas. Runtime envelopes are the existing worker dataclasses. No model, tensor,
backend import, executable search or subprocess starts at package import or
`INPUT_TYPES`. Backend binaries are external, explicitly selected absolute paths
in `OperationContext.versions`, or the corresponding node widgets.

## Recipes, versions and storage

`DEFAULT_RECIPE` is an owner-versioned JSON object:

```json
{"version":"kvd-normalize/1.0.0","resampler":"displayed_hold","fps":{"num":24,"den":1},"geometry":"preserve_display","sample_rate":48000,"audio_mode":"preserve","gap_policy":"hold","video_codec":"ffv1-nut"}
```

Only `sample_rate` (8000–192000) and `audio_mode` (`preserve`/`mute`) vary.
EOF comes from the last decoded frame's positive duration. Missing duration is
`AMBIGUOUS_MEDIA_TIMING` until the caller supplies an exact positive final-frame
duration in seconds, e.g. `versions['endpoint_duration']='1/24'`. This override
applies only when decoded EOF is missing; it is recorded in the probe receipt
and propagated into normalization. There is no container-duration/average-rate
fallback. Duplicate/backward displayed PTS and changing coded dimensions are
explicitly unsupported timing/geometry cases.

Algorithm versions: `kvd-decoded-pts/1.0.0`, `kvd-displayed-hold/1.0.0`,
`kvd-display-pad/1.0.0`, `kvd-balanced-windows/1.0.0`,
`kvd-disk-window/1.0.0`, `kvd-global-pcm/1.0.0`, `kvd-assembly/1.0.0`.
The built-in source policy is `kvd-native-source/1.0.0`; it records the pinned
core source revision and **source_only** evidence, never an installed or tested
H3 profile. Shared validation restricts this M1 profile to lattice `5+17*k`,
policy 124–345 frames, grid32, FPS24 and all padding under 15 seconds.

Temporal, spatial and assembly artifacts use foundation `cache_key` /
`cache_locator`: actual content and PTS hashes, recipes/policies, algorithm and
backend build versions determine identity. Private absolute paths and mtimes do
not determine identity. Temporal/spatial hits recheck content and their dependent
manifests; assembly currently re-verifies/re-encodes each requested export, even
at an existing assembly key. Prompt edits change generation keys while reusing
source/spatial preparation. Unchanged replanning preserves window IDs/records;
actual plan or active-result edits advance the Project revision for SaveProject.

Canonical/prepared video is FFV1 RGB in NUT because a millisecond time base cannot
represent every `j/24` exactly. Displayed SAR is baked into a square-pixel width
using half-up rounding, then an orthogonal rotation is applied once. Preparation
centers that displayed image without scaling on a grid32 canvas. Inverse crop
must already be applied to each successful useful render artifact. Reflected,
scaled, translated or nonorthogonal display transforms need a later policy.

`OperationContext.versions` supports positive `disk_quota_bytes` (default4GiB),
`working_set_bytes` (default256MiB for active Python RGB buffers), and
`timeout_seconds` (default1200 per owned backend child). The disk budget includes
known operation outputs/temporaries and nested probes; unrelated pre-existing
project files are not scanned or charged. Free space is checked before work.
Streamed PTS/selection rows, small metadata reads and disk artifacts keep RAM
independent of film frame count. External decoder/encoder memory is measured
separately. Cancellation checks run during hashing/frame/sample work and a
watchdog can interrupt a blocked owned pipe. Native Comfy interruption is consulted
only during a human-requested node execution. No queue API or model-loading path
is present. Temporary files are removed on ordinary cancellation/error; already
written media bytes without a successful manifest are inactive.

Preparation currently decodes/discards canonical frames from the start for an
exact index trim. It makes no approximate seek and no per-window FPS resample;
long-film speed optimization remains future work.

## Audio and export

All sample boundaries use `Q(f)=floor((f*Fs+12)/24)`. Source audio timestamps are
relative to the first displayed video frame: positive offset becomes silence,
negative offset is trimmed. Normalization creates one global s16 mono/stereo WAV
with exactly `Q(F)` samples, applying decoder-signaled priming. Unsupported source
channel layouts fail explicitly. No selected audio stream means a video-only
export; mute produces no soundtrack. Preserve with known source audio but missing
PCM fails rather than silently dropping sound. Scene decisions can override the
global mode. Generate accepts only already supplied, useful-trimmed matching PCM
artifacts; it performs no audio generation.

Full export copies `[Q(a),Q(b))` across contiguous technical windows without
rounding origins at their edges. Selected-only export concatenates selected
scenes, preserving contiguous audio runs. A run's output-origin phase difference
is at most one sample and is fitted once at its end, with a reported correction.
Discontinuous selections and audio-mode transitions are explicit run boundaries.
An optional sample-rate change resamples the whole global PCM once before slicing.
The final soundtrack is encoded once together with the final video. Actual decoded
sample count and codec skip/discard values are recorded; PCM is exact and encoded
audio duration tolerance is at most one video frame.

`DEFAULT_POLICY`:

```json
{"version":"kvd-export/1.0.0","codec":"ffv1-nut","selection":"full","odd_dimensions":"reject"}
```

`codec` also supports `h264-aac`; `selection` may be `selected`.
Odd H.264 dimensions fail unless `odd_dimensions='pad_even'` explicitly adds a
right/bottom pixel. The actual export dimensions are recorded, including this
codec padding. The result is an assembly `RenderResult` with CPU evidence and
no window/scene ID. Before export each supplied result must match the Project's
explicit active selection, successful status, generation key, exact ranges,
native/useful counts and geometry. Artifact bytes are hashed, receipt paths must
exist, and actual decoded useful PTS/geometry are independently re-probed. Missing,
extra, stale, changed or incomplete outputs fail with shared typed/redacted errors.
There is no automatic original-source substitution.

## Human manual wiring

These are real node classes, with import/portable checks described in the
[CPU receipt](validation/M1_MEDIA.md); no live ComfyUI workflow acceptance is
claimed. Every disk node asks for an existing local project folder, explicit
FFmpeg/ffprobe paths and resource budgets. Personal workflow paths stay local.

1. `KVD_ProbeMedia`: select the relative source file, absolute video stream index,
   and audio stream index (`-1` excludes sound). Inspect origin/EOF in its report.
2. Connect `source_media` to `KVD_NormalizeMedia`; choose preserve/mute and PCM rate.
3. Connect `probe` and `normalized` to `KVD_MediaProject`. Author the visible scene
   prompt and seed. An optional actual `KVD_RENDER_PROFILE` replaces the built-in
   checked source policy. This helper creates one scene; JSON/Project nodes retain
   responsibility for later explicit editorial edits.
4. Connect its `project` and `render_profile` to `KVD_PlanWindows`, then the planned
   project to `KVD_SelectWindow`. Select a zero-based index. Connect `window`,
   `canonical_media` and `spatial` to `KVD_PrepareWindow` for a disk artifact.
5. A separate later H3 owner must produce successful useful-trimmed RenderResult
   records. Preparation's artifact is not a generated result. There is no H3 node
   or finalize/control adapter in this task.
6. `KVD_SelectResults` accepts an explicit JSON array of those successful current
   records and replaces the active result map. Connect its Project to
   `KVD_AssembleExport`; choose full/selected, codec and odd-dimension policy.
   Optionally connect an explicit AudioTimeline. Output media remains on disk.

The owned presentation files register eight stable `KVD_` IDs through the shared
presentation API. English is the default; persisted Russian uses existing
`KVD.Language` and the shared setting/readback mechanism. Titles, help, labels and
tooltips translate; `.name`, port types, links, enum/seed/prompt values and custom
titles stay stable. A small owned CPU-status panel follows the same language and
shows measured counts/dimensions without claiming generation. No second preference
store, automatic execution, foreign-node customization or language-triggered I/O
was introduced. Visual appearance and native serialization still need the later
allocated human live gate.

The integrated [CPU receipt](validation/M1_MEDIA.md) records161 passed,
one POSIX-only skip on Windows and no failures. The six historical ac335 shared
assertion failures are resolved by the reviewed common tests imported from
exact c923. Shared files match that commit; no media-owned shared amendment was
made. The [existing draft stacked PR3](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/3)
and AO handoff carry the frozen candidate SHA/tree for independent media review.
Synthetic CPU exports do not establish H3, real-video or live UI acceptance.
