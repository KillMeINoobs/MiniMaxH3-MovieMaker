# M1 Canny and native H3 handoff

This is a source/CPU implementation candidate. Native Canny contour execution,
installed custom-node/workflow acceptance, checkpoint loading, GPU fit, H3
generation and human result acceptance are **NOT PERFORMED**. The supplied
[preparation-only workflow](../workflows/m1_canny_preview.json) and
[short generation workflow](../workflows/m1_short_v2v.json) are diagnostic.

The CPU assignment started from exact reviewed
`ac335b87c966b3353c5115c663d4344ff08c01a0`, descended from C0
`7960568eff779c8c35c3d28a985a243368b91c26`. An owned checkpoint was preserved
before normally merging the whole subsequently reviewed common commit
`c923d9e4292ea40e4a3f37f2feace8fa252eecb4`; integration commit is
`0d80cb7b0fe60fa290ec54f22971771b0b6fb345`.
[Common source/synthetic approval](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5415254811)
does not establish live foundation acceptance. No shared contract, manifest,
lockfile, discovery skeleton or media-owned file was edited by this adapter.

The coordinator subsequently released the whole reviewed media common
`69ed44577550b8545a40cc3209a488d9fcd13fda`. Normal merge
`74eb530c0fd9445a6bfb603a9c9182a982a5781b` preserves both the owned
`9185151fa583b64dfce445d5c16779e0d207c171` checkpoint and CM69ed history.
[Media source/CPU approval](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/3#pullrequestreview-5417990776)
is a dependency receipt, not H3 approval. All five media handlers and eight
media nodes are now present; owned I/O consumes their actual backend, decoded
PTS, global sample-boundary and result-selection helpers. Production media,
contracts, schemas and dependency files remain identical to CM69ed. Initial
obsolete ac335 assertions were resolved
through whole c923 integration, without editing or suppressing shared tests.

The final coordinator release also adopts two exact independently reviewed
local amendments through normal whole merges: media test-only
`88b8441894479a99ed5d79894c2e7eddcffac72e` at merge
`bf48c3764a9433c62d6fc696f13ef17fd13a760c`, then foundation
`f231a5180dc2ab0825860dbb5928d22862587e7e` (including reviewed c08) at merge
`8ed8d1fff53ed3af9417a93878f39fc0a6bf2d71`. The former keeps required media
handlers/classes/import safety while accepting owned extensions; the latter
retains strict native fixture comparison and explicitly authors its widget
sockets. Their local source/synthetic approval is not full H3/native/GPU
acceptance. Published media/foundation refs and PR2/PR3 remain unchanged.
The separate foundation owner has recorded its four-node registration,
roundtrip and fresh-page/Russian persistence check. Full visual foundation
acceptance remains incomplete. That receipt does not cover aggregate25-node
registration, these H3 workflows, native Canny, model loading or generation.

## Callable boundary

All four handlers are actual functions registered from owned `h3_nodes.py`
through existing auto-discovery. They retain the unchanged
[KVD-WORKER/2.0.0](../kmin_video_director/contracts/worker.py) signatures and
immutable schema/data 2.0.0 records. Optional packages import only during an
explicit operation, never in package discovery or `INPUT_TYPES`.

| Operation | Implementation | Observable behavior |
| --- | --- | --- |
| BuildControl | [canny.py](../kmin_video_director/controls/canny.py) | Exact prepared geometry/count, native Canny or explicit structural off, content-hashed disk RGB maps and recipe receipt |
| CompileWindowPrompt | [prompt.py](../kmin_video_director/adapters/native_h3/prompt.py) | Exact visible per-window text and UTF-8 digest; no hidden rewrite, bindings or context |
| ExpandNativeRender | [graph.py](../kmin_video_director/adapters/native_h3/graph.py) | Deterministic actual GraphBuilder expansion with native conditioning/sampler/decoders, checked ports/settings/resources and serial gate |
| FinalizeWindow | [finalize.py](../kmin_video_director/adapters/native_h3/finalize.py) | Exact decoded identity/count, useful trim, inverse spatial crop/resize, durable video/useful PCM/receipt/RenderResult and small finalized order token |

`REGISTRY.require_operation` dispatches these real implementations. The
foundation-only `require_runtime_capabilities(operation=...)` guard remains
unchanged; it is not a runtime implementation.

The 13 owned discoverable IDs are `KVD_H3Profile`, `KVD_ControlSettings`,
`KVD_BuildControl`, `KVD_CompileWindowPrompt`, `KVD_BindWindow`,
`KVD_ExpandNativeRender`, `KVD_FinalizeWindow`, `KVD_ControlPreview`,
`KVD_WindowGate`, `KVD_OrderedModel`, `KVD_OrderedClip`, `KVD_ControlImage` and
`KVD_NativeReceipt`. The last five are real native-expansion helpers, rather
than registered protocol/envelope classes.

## Canny recipe and native graph

The backend remains **`comfy-native-canny`**. The owned implementation version
is `kvd-native-canny/1.0.0`. Finite normalized thresholds must satisfy
`0.01 <= low < high <= 0.99`, matching native widget limits and Kornia's ordered
threshold requirement. RGB bytes become float `[1,H,W,3]` in 0..1 and call the
actual native `Canny.execute`; that operation chooses native devices/dtypes and
Kornia's Canny edges. Only the fitted content rectangle is processed; declared
canvas padding is restored to black. Adjacent identical prepared frames reuse
their computed map. Final disk maps contain exactly `N*H*W*3` binary RGB bytes.

Native source SHA256, actual Torch/Kornia versions, thresholds, prepared content,
spatial transform and frame count determine the map cache key. The map's
`probe_version` also binds the implementation receipt digest. Strength/schedule
change generation identity while reusing the same extraction. Paths and mtimes
are resolution hints: identical regeneration/relocation preserves generation
identity; content, stream, probe/decoder or algorithm revisions invalidate it.
No FFmpeg/stdlib edge detector substitutes for absent native Canny dependencies.
The isolated verification environment lacks native Comfy/Torch/Kornia, so its
native contour case is explicitly skipped, **not a mock contour PASS**.

Every inference window has 24 FPS and the upward `5+17*k` lattice, with
124..345 frames including all padding/context. 345/24 is below 15 seconds.
The initial path requires no context, continuation, references or bindings.
Structural maps connect only to `MiniMaxH3FunControlNetApply.control_video`.
Source RGB, appearance/reference sockets, audio-guide and inpainting sockets
remain separate; the latter are absent in the emitted first graph. Structural
off removes the map/patch branch and retains native prompt/seed/sampling/decode.

The checked source profile pins Ref2VA, the template's Union v1 checkpoint,
5 injection blocks at `[0,10,20,30,40]`, 49 control channels and pre-normalization.
Base/patch AdaLN basis versus full width is checked explicitly. Union v2's
10-block/post-normalization layout is recognized for rejection/metadata tests;
it is not an approved alternative initial profile. Unknown revisions, incomplete
keys, metadata mismatches or unsupported native schema changes fail honestly.
UNET `weight_dtype` must be `default`; unapproved fp8 overrides return
`MODEL_INCOMPATIBLE` before expansion. CLIP type is `minimax`, device `default`.
The explicit initial sampling is `res_multistep`, `simple`, 20 steps, full
denoise, video shift 12 and audio shift 3. Changes must remain schema-valid and
change the frozen profile/generation identity.

GraphBuilder produces native links into BasicGuider, BasicScheduler,
RandomNoise, KSamplerSelect, SamplerCustomAdvanced and the native video/audio
VAEs. No hidden sampler, HTTP self-queue or custom model-management path exists.
A decoded receipt is insufficient to order a later window: a durable finalized
token with matching Project/plan/ordinal/useful endpoint is required. It contains
no tensor. This candidate supports one selected window per manual workflow;
native cache lifetime and long-run memory bounds remain unmeasured.

Finalization uses the reviewed bounded backend and real decoded-PTS probe for
useful video (`kvd-h3-rgb-io/2.0.0`, `kvd-useful-finalizer/1.1.0`). Preserve/mute
leave the Project-global PCM and original source offset untouched; generated
native audio is never silently substituted for the source soundtrack.

The generated-audio bridge (`kvd-h3-generated-pcm/1.0.0`) accepts exact native
32000 Hz stereo `[1,2,L]` AUDIO. Pinned H3 temporal shape uses 40 latent ticks
per second and the audio VAE decodes 800 samples per tick:
`L = round(N*40/24)*800`. This differs from exact video duration by a bounded
rounding amount. The bridge trims the local useful interval, explicitly pads
any declared native endpoint shortfall, resamples once to the Project's
rate/channel layout and fits the measured endpoint to the **absolute**
`Q(b)-Q(a)` count, where `Q(f)=floor((f*Fs+12)/24)` comes from reviewed media.
Every correction is reported; no per-window phase offset or source-origin reset
is invented. Native PCM bytes, versions, policy and attempt bind durable artifact
identity. Settings must match the explicit global AudioTimeline sound decision.

Finalize collects actual results through reviewed `select_results`, adds their
artifacts to Project.media, retains prior attempt history and emits a current
JSON **array** on the stable `result_json` STRING output. `KVD_SelectResults`
consumes that array before Save/Assemble. Distinct attempts retain distinct
logical artifact IDs even when their encoded bytes are identical. Missing
windows remain partial and cannot export through source fallback. Constructed
RGB/PCM tests prove this CPU path only; native tensor conversion, H3 audio
decoding, generation and long-run GPU memory behavior remain unperformed.

## Public source and resource pins

Existing [research/license ledger](RESEARCH.md) remains authoritative. A narrow
recheck was needed because the read-only schema handoff's core differs from the
research pin. No repository clone, weight download or native execution occurred.

| Source | Exact inspected revision and purpose |
| --- | --- |
| [Native core](https://github.com/Comfy-Org/ComfyUI/tree/daeb5e53681e2b10a3f0727d9ec5bc90784bee10) | `daeb5e53681e2b10a3f0727d9ec5bc90784bee10`: selected Canny/H3/model-patch/GraphBuilder/sampler/audio/model-detection/model/controlnet/loader/expansion source; core GPL-3.0 |
| [Native VAE configuration](https://github.com/Comfy-Org/ComfyUI/blob/daeb5e53681e2b10a3f0727d9ec5bc90784bee10/comfy/sd.py), [audio VAE](https://github.com/Comfy-Org/ComfyUI/blob/daeb5e53681e2b10a3f0727d9ec5bc90784bee10/comfy/ldm/minimax/audio_vae.py) | Same GPL-3.0 core pin: 32 kHz stereo output, 800-sample hop and waveform geometry inspected without import/execution |
| [Research core](https://github.com/Comfy-Org/ComfyUI/tree/b87fe48b0491425f682f7ffdaed56d0387cb6c5d) | `b87fe48b0491425f682f7ffdaed56d0387cb6c5d`: existing authority; Canny/H3/model-patch/GraphBuilder/controlnet raw files matched the newer pin byte for byte |
| [Native template](https://github.com/Comfy-Org/workflow_templates/blob/0e5c5efb32ba6f3365d6da07da64aaf668157042/templates/video_minimax_h3_fun_controlnet_union.json) | `0e5c5efb32ba6f3365d6da07da64aaf668157042`, MIT; source/profile selection, not our runtime receipt |
| [Converted component metadata](https://huggingface.co/Comfy-Org/MiniMax-H3/tree/e5eb578a89295337b8ff433a035929ce0279e0b6) | `e5eb578a89295337b8ff433a035929ce0279e0b6`; card and exact-revision public LFS file SHA256/size metadata, no weight access |
| [Union v1 card](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union/blob/9df91437f0890b20f8a0b07c1d9500648cfcbf44/README.md), [Union v2 card](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union-2.0/blob/7d2c95de2e351ed6a0b360af45f62daa04c26f88/README.md) | Existing pinned separate Community License and v1/v2 scope; no equivalent-checkpoint or combination claim |

The component names/digests/sizes are in
[components.py](../kmin_video_director/adapters/native_h3/components.py).
`KVD_H3Profile` first checks dropdown availability, then explicitly selected
regular safetensors headers and complete SHA256/size against those public pins.
It never loads a model. Source-only metadata does not certify quantization
kernels, native loader completeness or GPU fit. Core code and model weights
have separate licenses; this handoff does not change the project's license.

The separate runtime owner provided raw object-info metadata for 32 selected
classes with real required/optional/hidden inputs, enum options, output slots
and V3 autogrow metadata. Its SHA256 is
`b5d9ffab1130ebaf98cf1cfecda529e7c8a3b0c19cd57894e982ed12142ed34d`;
the provenance receipt SHA256 is
`b974829e302a612b97d57b8290fe3919c4502a07ec7a37b4eff90ccc3213b1de`.
Private artifact paths and machine/session diagnostics stay in AO. A malformed
handoff envelope/section/core/port returns redacted `MODEL_INCOMPATIBLE` before
GraphBuilder or model access. Dropdown names alone are not weight compatibility.
The separate immutable PreviewImage supplement has SHA256
`0751c1d78c8ba97a23a8167de253f63766ce43b041e1e866820fa4463081916c`
and receipt `b99b8762014943eb58dd38a75787422ebfbe799fc63a12664269eee3bb020f03`.
Its actual IMAGE output slot is preserved in both artifacts. This is read-only
schema evidence, not PreviewImage execution or installed adapter acceptance.

## Human short-workflow setup

Do these steps only after independent H3 source review and separately allocated
installation/native-node preflight. Both artifacts have static checks against
the actual merged classes and native handoffs; **neither has been loaded or
queued**. Output nodes remain muted and paths remain blank for human setup.
The reviewed frontend1.53.6 rule materializes definition-owned widget inputs
after nonwidget inputs. Both artifacts now explicitly author those sockets,
including their stable widget-name association and unlinked defaults. Existing
link endpoint indices, output slots, widget values, prompts and titles are
preserved. Static metadata checks reject missing/wrong/reordered widget sockets;
native H3 workflow load/roundtrip/layout remains unperformed.

### Phase A: video → CFR24 → window → native Canny preview

Use [m1_canny_preview.json](../workflows/m1_canny_preview.json). Its 10 actual
node declarations and 15 typed links have **no H3Profile, checkpoint loaders,
native H3 expander or sampler**. `KVD_MediaProject` supplies its existing built-in
source-only shape policy (24 FPS, grid32 and bounded native lattice) without any
model components. `KVD_ControlSettings` authors the Canny extraction recipe from
that shape policy; generation checkpoint compatibility is a separate later check.

1. Set the human's existing project folder on each disk node, select the relative
   `test-1.mp4` filename (or another explicitly chosen file) and its actual
   absolute video stream. This worker did not open/copy/decode that asset.
   Configure the existing absolute FFmpeg/ffprobe paths and finite budgets.
   Preparation defaults to mute and audio stream `-1`, so source audio is not
   needed for this structural inspection.
2. After native Canny and installed node preflight, enable only PreviewImage's
   initially muted output. Queue this preparation graph through the normal
   native client. No H3 weights are a dependency of this graph.
3. Inspect Probe/Normalize reports, the exact CFR24 count and plan. Select
   `window_index=0` (the first bounded window); multiple planned windows are
   acceptable for this first preview, which is not a whole-film render.
4. Inspect one actual Canny frame. Set `preview_frame` within the reported native
   frame count to inspect another frame. Check structural contours and declared
   black canvas padding. Dependencies/source provenance must match native Canny;
   an unavailable backend is a typed blocker. This CPU candidate has not run
   the native contour or this human preview.

The absent baseline H3 checkpoint does not block Phase A, and Phase A does not
verify H3 resources, loading, GPU fit or generation quality.

### Phase B: separate H3 resource preflight and human generation

Use [m1_short_v2v.json](../workflows/m1_short_v2v.json). It deliberately adds
the separate H3Profile and native loader/expander/finalizer branch: 23 nodes and
43 typed links, including the existing media SelectResults node. Keep its
output nodes muted until the following explicit setup/resource checks pass.

1. Use an explicitly chosen short local source in an existing project folder.
   Start with one scene around 5–10 seconds, small display geometry and no cuts.
   Full export requires `KVD_PlanWindows` to report exactly one window. If the
   human's test file plans multiple windows, select index 0 for a bounded H3
   check and keep Assemble muted: the saved Project is then explicitly partial,
   with other windows unrendered. No automatic source file copy/search
   occurs. Set the relative source filename and actual absolute video/audio
   stream indices (`-1` excludes audio) in `KVD_ProbeMedia`.
2. Set the same existing project folder and explicit existing FFmpeg/ffprobe
   paths on every disk node. Paths in the committed workflow are deliberately
   blank. Keep budgets finite/positive; a too-large native map returns
   `RESOURCE_LIMIT`, not a fit promise. Preserve source audio or choose mute.
   The initial graph uses global PCM 48000 Hz for preservation; native H3 audio
   decoder output is a separate role and is not the preserved source soundtrack.
   Selecting audio stream `-1` excludes source audio, even in preserve mode;
   explicitly choose its actual absolute stream index to retain it.
3. Select the fresh read-only native schema handoff in `KVD_H3Profile` and
   `KVD_ExpandNativeRender`. Use these exact source-template checkpoint files
   in the helper and their corresponding native loaders:

   | Native folder/loader | Required file |
   | --- | --- |
   | diffusion_models / UNETLoader | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` |
   | text_encoders / CLIPLoader | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
   | vae / VAELoader | `minimax_h3_video_vae_int8_convrot.safetensors` |
   | vae / VAELoader | `minimax_h3_audio_vae_fp32.safetensors` |
   | model_patches / ModelPatchLoader | `minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors` |

   The supplied resource metadata lacks the first file. This is a concrete
   **BLOCKED** resource gate. The human must separately arrange the exact file
   through their authorized model workflow; no substitution or download was
   performed. Select native UNET dtype `default`, CLIP type `minimax`, CLIP
   device `default`. Off still requires the exact base/text/VAEs.
4. Choose `canny` in both profile and structural settings. Default thresholds
   are 0.4/0.8; strength 1 and schedule 0..1 are visible/editable. Author the
   scene text in `KVD_MediaProject` and the exact window text in
   `KVD_CompileWindowPrompt`. Its prompt is deliberately empty until edited.
   `KVD_BindWindow` freezes the actual text/map/profile/settings key.
   Appearance/reference/context/guide/inpaint inputs stay empty.
5. For control inspection, keep Finalize/Assemble/Save outputs muted and enable
   only the native PreviewImage output. It receives one actual computed Canny
   frame through `KVD_ControlPreview`; inspect contours and black canvas pad.
   Native Canny dependencies must exist and match the recipe. Preview failure
   is a blocker, not evidence that an alternate edge backend is acceptable.
6. For the human H3 run, enable Finalize, and optionally SaveProject. Enable
   Assemble only for the exactly-one-window complete plan. The normal native
   queue performs the expanded sampler and
   decoding. Inspect progress/cancel behavior and actual useful result counts,
   crop, image quality and audio. Finalize's Project and current result array
   feed SelectResults; its selected Project feeds Save/Assemble. The linked
   Normalize AudioTimeline is the original global preserve/mute policy.
   An export with missing coverage must fail; keep it muted for a first-window
   check of a longer source. Choose a new Project filename
   for a new save; replacing an existing Project is an explicit human choice.
   Use a new request ID or increment attempt to retain separate manual attempts.
7. After a successful real run, retain workflow/model selections, native graph,
   exact counts/fingerprints/result receipts, output and human observations.
   Record real runtime/GPU evidence separately through M1-04. An off comparison
   switches structural settings/profile to off and replans/rebinds; disconnect
   the Canny preview output. Off removes structural patching, without making
   source RGB an appearance reference.

The supplied graph uses source preservation (or explicit mute), not a generated
sound selector. Generated useful PCM is implemented and tested through the
unchanged callable contract using constructed native-shaped PCM. Using that
policy requires an explicitly configured portable Project with matching
Settings/global AudioTimeline decision, replanning/rebinding and the matching
Project timeline at Assemble; do not leave the original preserve-timeline link
while changing only a window mode. A mismatched decision fails
`AUDIO_SYNC_MISMATCH`. This does not imply a human generated-sound test occurred.

The shared persisted `KVD.Language` selector defaults to English. Russian
translates the 13 owned node titles, fields, help, statuses and typed errors.
Stable IDs/socket keys/types/enum values/prompt/seed/links/custom titles remain
unchanged; foreign nodes remain untouched. Actual language storage/readback
helpers are tested with the real shared module. Browser layout and native
save/reload still require the separate live gate.

Verification details and unperformed checks are recorded in
[M1_ADAPTER.md](validation/M1_ADAPTER.md). Publication is released as one draft
stacked on the exact CM69ed media branch. The
[completed d5be source/CPU review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/4#pullrequestreview-5419547665)
requested only H4/H5. Correction commit
`cd38bf8e6a77d776aa0e18c6785f85524e004307` adds typed redacted rejection for
nonfinite native schema options and malformed dtype containers, preserving
valid schema/header fingerprints. The current owner Python run passes398
with the native-Canny/POSIX skips;54 frontend passes are retained at unchanged
blobs. Independent correction review and separate human/native/GPU gates remain
pending. Manual workflow artifacts and setup instructions are unchanged.

## Original released implementation plan (historical)

Source dependency: `ac335b87c966b3353c5115c663d4344ff08c01a0`, descended
from accepted C0 `7960568eff779c8c35c3d28a985a243368b91c26`. Independent
review 5413276074 approved source/CPU evidence only. Full foundation live
acceptance remains blocked. The implementation assignment separately releases
owned CPU work; it does not release shared runtime or generation.

## Scope and design

Implement the four unchanged KVD-WORKER/2.0.0 operations: BuildControl,
CompileWindowPrompt, ExpandNativeRender and FinalizeWindow. Import immutable
records and runtime envelopes from foundation. Register actual implementations
and nodes through owned `nodes/h3/*_nodes.py`; use shared presentation and
verified KVD.Language helpers. Optional runtime packages remain lazy.

The first recipe uses Canny or explicit structural off, authored visible text,
empty reference/guide/inpaint inputs and no continuation. A bounded window has
24 FPS, a profile-derived upward `5+17*k` length between 124 and 345 including
all padding, exact canvas geometry and exact useful finalization. Native
conditioning, sampling, decoding, interruption and model management remain
native graph operations. Missing schemas/models/backends fail explicitly.

## Implementation steps

1. Inspect narrowly pinned primary native H3, Canny, graph-expansion, sampler
   and model metadata. Record public source/license provenance. Write failing
   owned tests for thresholds, contour geometry, authored text/digests, profile
   rejection and no-reference policy; implement those pure CPU portions.
2. Add deterministic native graph creation and required class/port/link/schema
   checks. Verify observable graph settings, off behavior, serial ordering and
   cancellation against pinned source and the separately supplied read-only
   installed-schema handoff. Implement checked durable useful finalization;
   label synthetic decoded outputs and CPU evidence honestly.
3. Add import-safe discoverable nodes and scoped EN/RU presentation. Test
   actual registrations, signatures, unchanged semantic data/custom titles,
   status/help and failures. Document callable fields and manual setup.
4. Integrate actual media helpers only after an explicitly supplied reviewed
   common SHA containing media. Produce `workflows/m1_short_v2v.json` from real
   interfaces, labelled diagnostic until installed preflight and human results.
5. Run the owned CPU/schema/import/frontend checks in an isolated environment
   with unchanged verification lock. Report obsolete shared assertions at the
   initial dependency separately. Verify brief/ledger and owned diff, freeze
   checked local commits, and await the coordinator's exact PR base/ref before
   publishing the one authorized draft candidate for separate review.

No H3/GPU/video-generation result, installed node, usable native graph or GPU
fit is claimed by this plan. M2/M3 and long-run memory acceptance remain gated.
