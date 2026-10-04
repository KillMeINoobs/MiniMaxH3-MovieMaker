# Proposed node collection

**Complete proposed inventory for the stated product, not registered nodes.** Display names and logical types may change during foundation review. These are responsibilities exposed to users, not a promise of one Python function/class per row. Small preparation/finalization nodes may be nested in native expansion, while the timeline and prompt/reference panels may share the main project node. Native ComfyUI nodes stay visible in expanded graphs. No extension or executable workflow exists; **GPU NOT PERFORMED**.

The user follows import → scenes/prompts → optional identities → window/control/render → review/export. [Direction](PRODUCT_DIRECTION_V2V.md), [contracts 2.0.0](CONTRACTS.md), [architecture](ARCHITECTURE.md), [workflow specification](WORKFLOW_SPEC.md) and [task journal](tasks/INDEX.md) define acceptance and ownership. Logical types are versioned manifests/IDs unless explicitly a bounded IMAGE/AUDIO/LATENT socket.

## Import and timeline

| ID / proposed node | Role and inputs | Outputs | First milestone / owner |
|---|---|---|---|
| N01 Project | Create/load validated project; project-relative asset registry, saved state | Project snapshot, validation report | M1-01 foundation; UI consumer M2-01 |
| N02 Import Video | Explicit approved local selection and stream choices; copy/link policy | Source MediaRef, timing/display/audio probe | M1-02 media |
| N03 Normalize CFR24 | Source MediaRef, normalization policy, cancel token; automatically requested on add | Disk canonical media, F/PTS/drop/hold manifest, audio timeline | M1-02 media |
| N04 Source Preview | Canonical manifest and thumbnail/proxy budget | Player/proxy/thumbnail handles, frame cursor | M2-01 editor; consumes M1-02 media |
| N05 Detect Shot Boundaries | Canonical media, detector/threshold/min-length recipe; streamed pass | Scored DetectionProposal list in frame coordinates, overlay | M2-03 scene intelligence |
| N06 Scene Timeline | Project/proposals; add/move/delete/numeric markers, selected scene, authored prompt | Revised Project/Segments, selection and edit events | M2-01 editor; proposal overlay M2-03 |

A proposed detected cut becomes an editorial boundary only after acceptance. Technical windows appear as a separate overlay; moving a cut replans affected windows. No large all-video IMAGE output from import/preview.

## Scene prompts and subject appearance

| ID / proposed node | Role and inputs | Outputs | First milestone / owner |
|---|---|---|---|
| N07 Analyze Scene | Segment/canonical media; bounded frame/time sampler; configured VLM profile; user intent | SceneAnalysis with coverage, observations, uncertainties and draft facts | M2-03 scene intelligence |
| N08 Subject Image Library / Bindings | Explicit image MediaRefs; stable subject IDs, target appearance, scene presence | Per-scene ReferenceBinding set and binding preview | M2-04 identity owner; foundation types first |
| N09 Scene Prompt Studio | User prompt + optional analysis + binding metadata + style/audio intent; optional text enhancer | Editable PromptRecipe draft, provenance/validation, accepted revision | M2-03 scene intelligence; identity integration M2-04 |
| N10 Plan Legal Windows | Valid Project/Segments, capability profile and enabled continuation policy | Ordered GenerationWindows, useful coverage and cost estimate | M1-02 planner; context extension M2-05 |
| N11 Compile Window Prompt / References | Accepted scene recipe, window useful/context/pad ranges, binding set and guide pin | Exact H3 prompt, local timing map, physical socket/label manifest, errors | M1-03 authored prompt path; M2-03/04 structured path |

N07 is vision inference; N09's enhancer is text/metadata inference; native H3 CLIP/Qwen conditioning belongs in N15. Optional automation failures keep manual editing available and visible. An analyzer finding does not silently replace an accepted user prompt or register source video as an appearance asset.

## Structure and native rendering

| ID / proposed node | Role and inputs | Outputs | First milestone / owner |
|---|---|---|---|
| N12 Prepare Window | One GenerationWindow, canonical disk handle, SpatialTransform | Exact bounded prepared manifest and materialized IMAGE `[N,H,W,3]` when needed | M1-02 media |
| N13 Canny Control | Prepared content, fixed thresholds and shared geometry | Exact canvas-sized Canny IMAGE/maps on disk, preview/fingerprint | M1-03 control/adapter |
| N14 Additional Structural Control | Prepared manifest; selected validated Depth/Pose/Gray profile; mixed recipe only if proven | Versioned map manifest, temporal calibration, preview, capability report | M3-01 control owner; optional dependencies |
| N15 H3 Conditioning | Compiled prompt/physical references, exact N/H/W, model/CLIP/video/audio-VAE links | Native CONDITIONING + joint AV LATENT | M1-03 native adapter; refs M2-04 |
| N16 Native H3 Window Render | Profile, native model links, maps, conditioning/latent, order token | Expanded native sampler/decoder result links and scoped progress | M1-03 adapter; real proof M1-04 |
| N17 Continuation Policy / State Load | Current window and predecessor result/state, cut/group IDs, compatible profile | Verified bounded state or explicit reset; dependency token | M2-05 continuity owner |
| N18 Apply Motion Context | Verified state, current native CONDITIONING/LATENT, compatible VAEs; tested context budget | Conditioned native links, actual overlap/trim manifest | M2-05 optional tested adapter |
| N19 Checkpoint Continuation State | Completed native AV latent plus window/profile/useful mapping | Atomic project-relative ContinuationState artifact/ID | M2-05 continuity owner |
| N20 Finalize Window | Decoded IMAGE/AUDIO, original window, observed trim/spatial map, attempt | Checked RenderResult, useful disk AV, order token, counts/receipts | M1-03 adapter; context trimming M2-05 |

N15/N16 wrap/expand **existing** `MiniMaxH3ReferenceToVideo` (empty refs is allowed), `MiniMaxH3ImageToVideo` for later keyframe modes, `MiniMaxH3SigmaShift`, `ModelPatchLoader`, `MiniMaxH3FunControlNetApply`, ordinary guider/sampler/scheduler and native AV decode. The exact emitted classes/schemas are pinned per profile, not invented here. N13 can reuse native `Canny` through expansion after geometry preparation. N17–N19 are absent/bypassed in M1. N20 is the single authority for trimming; never trim the overlap twice.

Source RGB never enters ref/guide/inpaint sockets implicitly. Appearance images enter explicit reference sockets via N11/N15; continuation is explicit keyframe/audio state via N17/N18. Canny+Depth/Depth+Pose remain disabled candidates until a matched backend has real support evidence.

## Run, recover, review and export

| ID / proposed node | Role and inputs | Outputs | First milestone / owner |
|---|---|---|---|
| N21 Run Selection | Frozen snapshot, selected scenes/all, validated plan, disk quota | Serial owned native prompts, request IDs and durable ledger/progress | M2-02 runner |
| N22 Resume / Retry | Ledger + native queue/history + artifact fingerprints; failed/stale selection | Reconciled retry plan; continuation-dependent invalidation | M2-02 runner; context chain M2-05 |
| N23 Assemble / Export | Ordered chosen valid results, global AudioTimeline, export codec policy | Final file + exact frame/PTS/sample/dimension/hash report | M1-02 assembly; GPU results M1-04; UI M2-02 |
| N24 Review / Compare | Source, map, controlled/control-off results; boundary/identity samples | Synchronized local previews and recorded human judgment | M1-04 evidence; editor integration M2-02/04/05 |
| N25 Workflow Project Save / Load | Serialized versioned Project + workflow, project-relative assets | Portable project/workflow bundle, missing/relink report | M2-01 state; distribution assets M2-06 |
| N26 Capability / Resource Preflight | Model/node/frontend identities, requested controls/refs/context, declared budgets | Actionable source/load/GPU capability states and estimates | M1-03/04; later adapters extend under foundation contract |
| N27 Create-Video Mode Settings | T2VA/I2VA/FL2VA/L2VA/Ref2VA authored prompt and explicit references/keyframes | Valid mode recipe and native conditioning choice | M3-02 creation-mode owner |
| N28 Workflow Setup / Validation | Real workflow variant, installed versions/schemas and explicit media relink | Missing-node/model report and accepted workflow validation receipt | M2-06 workflow owner; M3 owners update variants |

No separate global-memory purge node is a product requirement. Owned analyzer/enhancer teardown and native model offload are execution responsibilities with measured budgets. N26 never auto-installs/downloads or changes the user's environment. Cancellation is a real owned-run action of N21, not an unrelated all-project stop button.

## Ownership and delivery boundaries

Foundation exclusively owns shared contracts, registration, package manifests/dependencies/lockfiles and initial skeleton; all node groups consume its **actually checked common commit**. Media owns N02/N03/N10/N12/N23 CPU behavior; adapter owns N11's initial manual path and N13/N15/N16/N20/N26. Editor owns N04/N06/N25 and agreed presentation hooks. Runner owns N21/N22 and run/review integration. Scene intelligence owns N05/N07/N09 and structured N11 integration. Identity and continuity owners extend their own adapter areas after preceding common commits. Workflow release owns real assets/documented setup and end-to-end acceptance, not shared schema redesign.

External reuse is selective: native H3/Canny/graph execution first; enhancer optional through a pinned manifest/text adapter; Motion-Context only through a tested state adapter; DaSiWa visual ideas; optional validated preprocessors later. No third-party runtime or source code is imported in M0. Licensing and incompatibilities are recorded in [RESEARCH](RESEARCH.md#licenses).
