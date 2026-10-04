# Product direction — V2V first

This addendum records the latest user direction for M0-V2V-REVISION. It takes priority over conflicting scope/order statements in the [original brief](PROJECT_BRIEF.md), whose bytes remain unchanged. This revision is research and documentation only: **no extension, implemented contract, ready workflow or runtime result exists; GPU NOT PERFORMED**. The first M0 documentation base is `1bfcc50e204797862b2bbc014fce00e4694c122c`, published separately from main; its parent is `8e8cf7253862f94b7787d7065babf2878064ef82`. This revision does not integrate either into main.

## Intended product

A complete local ComfyUI node collection for creating and transforming video, with timeline editing and a supplied, tested, usable workflow. The main first mode is **video-to-video (V2V / our VID2VA label)**: gameplay or a low-poly Blender render becomes photorealistic cinematic video while preserving intended action, composition and camera motion through structural conditioning. Quality is a target to evaluate, not a guarantee. [Higgsfield](https://higgsfield.ai/) is inspiration for outcomes and workflow clarity; no equivalent system, API access or integration is claimed.

Adding video automatically produces real CFR **24 FPS** media while preserving playback speed and recording duration quantization. Any duration is planned and processed in bounded legal H3 windows, subject to disk, memory and time budgets. Neither all-video tensors nor unlimited practical resources are acceptable. Original media stays untouched.

The user marks, moves and edits scenes on a timeline. Automatic shot detection may propose boundaries that the user reviews and corrects; detecting a visual cut does not prove a narrative scene boundary. Editorial scenes and technical inference windows are different objects. Each scene has its own editable prompt, with visible inherited settings and a visible final per-window prompt.

Prompt generation and enhancement are important product requirements. An optional, appropriately sized **Qwen vision-language analyzer** inspects bounded samples covering each scene and drafts descriptions of action, camera, environment, subjects and style. A separate **text enhancer** can convert reviewed descriptions into H3 blocks. H3's embedded Qwen encoder remains generation conditioning; it is not our scene-analysis service. The named [Prompt Enhancer](https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer) is an integration candidate with actual interfaces and limitations documented in [research](RESEARCH.md#prompt-enhancer).

Optional **reference images** bind a game character or other subject to its intended photorealistic identity/appearance across scenes. The structural V2V path must remain usable with no references. Source RGB used for probing, analysis or control extraction is not automatically an appearance reference, guide or inpaint input. Stable subject/asset IDs and per-window physical bindings must agree with prompt labels.

Consistency is central: test continuation inside a continuous shot, deliberate resets at cuts, and identity across cuts separately. [Motion-Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context) is a continuation candidate, not a guarantee of perfect continuity or an automatically compatible execution backend. Controls include evidence-gated Canny, Depth, Pose, Gray and requested Canny+Depth/Depth+Pose investigations. Mixed support cannot be established by adding or blending images.

The [DaSiWa UI](https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes) is a visual reference. Transfer useful patterns into a ComfyUI extension without adopting its runtime or imposing its reference semantics. A ready workflow must eventually contain real registered nodes and tested wiring; [WORKFLOW_SPEC](WORKFLOW_SPEC.md) is currently a specification, not such an asset.

## Explicit supersessions

| Earlier brief / first M0 | Latest direction and revision |
|---|---|
| Start by selecting equal-priority T2VA/I2VA/FL2VA/REF2VA/VID2VA modes | V2V organizes the architecture and first workflow. Other creation modes remain eventual deliverables, after the V2V product gates. |
| LLM prompt rewriter excluded from early stages; first architecture deferred rewriting | Superseded as product scope. Scene analysis, structured draft prompts and optional enhancer integration are explicit M2 requirements. M1 can use authored prompts for its short proof; M0 remains docs only. |
| References and movement/audio continuation placed broadly in M3 | Optional appearance-image binding and within-shot continuation are central V2V M2 gates, after the short GPU proof and reliable editor/runner. Cut resets and cross-cut identity are separate acceptance cases. |
| Minimal timeline viewed mainly as a small editor | It is a step toward the complete node collection and ready workflow; scene detection proposals, prompt review and reference/continuity state belong in the product design now. |
| Union/Gray/mixed controls only generic candidates | Evidence matrix identifies native single-control support and v1/v2 differences; requested mixed pairs receive an explicit research/validation outcome before enablement. |
| First M0 publication text asked for a draft PR | This assignment authorizes docs commit and own-branch SSH push plus compare link. The recorded PR/auth blocker is not retried; no PR claim, creation or main merge is part of this revision. |

Unchanged: Windows target RTX 5070 Ti 16 GB / 32 GB RAM, fit **UNVERIFIED**; no mandatory WSL; first short Canny/native-H3 proof before a large timeline; real 24 FPS; exact useful frame/sample accounting; strict inference duration **<=15 s including padding and continuation head**; no-reference V2V; original-source preservation; separate audio export policy; normal ComfyUI execution/model management. No supplied video or private workflow is assumed available.

## Requirements reconciliation

**F** source fact, **I** inference, **P** proposed product/design, **U** unknown. Document coverage is not runtime evidence. Node IDs below refer to the complete **proposed** [catalog](NODE_CATALOG.md); cards are linked in the [journal](tasks/INDEX.md).

| ID | Requirement / correction | Documents | Nodes | Outcome / evidence status |
|---|---|---|---|---|
| V01 | Complete collection; V2V first; cinematic transformation goal; Higgsfield boundary | This addendum; README; PLAN | N01–N28 | M1-04 visual comparison; M2-06 delivery; M3-02 creation modes. P; quality U. |
| V02 | Automatic real CFR24, speed/PTS/rotation/SAR, unchanged input | CONTRACTS media/spatial; ARCHITECTURE | N02–N04 | M1-02 synthetic media + actual decoded receipts. F backend capability; P policy; runtime not performed. |
| V03 | Arbitrary duration, bounded windows/RAM/GPU/disk, <=15 s with all overhead | CONTRACTS windows/cache; RESEARCH constraints; PLAN | N03, N10–N12, N20–N24 | M1-02/04, M2-02/05. F lattice; I 345 maximum; long-run resources U. |
| V04 | Editable scenes distinct from technical splits; automatic proposals/manual correction | ARCHITECTURE scenes; CONTRACTS Segment/DetectionProposal | N05–N07, N10 | M2-01 manual editor; M2-03 cut proposals. F detector interfaces; P integration. |
| V05 | Per-scene prompt, inherited edits, visible exact window prompt | CONTRACTS PromptRecipe; WORKFLOW_SPEC | N06, N09–N11 | M2-01/03. P; no hidden rewriting. |
| V06 | Qwen scene vision with bounded temporal coverage; enhancer/encoder separation | RESEARCH analysis; CONTRACTS SceneAnalysis | N07–N09, N11 | M2-03 local Transformers or explicitly configured multimodal endpoint. F interfaces; target fit/accuracy U. |
| V07 | Named enhancer source, blocks/modes/manifests, local/API/fallback, dependencies/memory/license | RESEARCH prompt-enhancer; CONTRACTS PromptRecipe | N09, N11 | M2-03 optional adapter + manual/model-free fallback. Source F; integration P; reclaim U. |
| V08 | Optional image identity/appearance binding across scenes, stable labels | CONTRACTS ReferenceBinding; RESEARCH conditioning | N08, N11, N15 | M2-04 + M2-06 identity workflow. Source co-wiring I; GPU quality U. |
| V09 | No-reference structural path; RGB/ref/inpaint roles separate | ARCHITECTURE adapter; WORKFLOW_SPEC | N12–N16 | M1-03/04 mandatory empty-ref path; M2-04 regression. F sockets; runtime not performed. |
| V10 | Native Fun ControlNet, model/version/tensor compatibility | RESEARCH native/control matrix; CONTRACTS profile | N12–N16, N26 | M1-03/04, M3-01. F source layouts; installed loading U. |
| V11 | Canny/Depth/Pose/Gray and mixed Canny+Depth/Depth+Pose evidence | RESEARCH control matrix; NODE_CATALOG | N13–N14, N26 | M1 Canny; M3-01 validated singles + documented mixed decision. Singles F; mixed U, disabled. |
| V12 | Within-shot continuation video/audio, overlap trimming, limits/license | RESEARCH motion-context; CONTRACTS ContinuationState | N17–N19, N22 | M2-05 measured combination gate. F code mechanisms; combined behavior U. |
| V13 | Cut reset separate from identity across cuts; no perfect-consistency claim | CONTRACTS Segment/ContinuationState; PLAN | N06, N08, N17–N19 | M2-04/05. P policy; visual outcome U. |
| V14 | DaSiWa look, screenshot/frontend evidence, actual frontend feasibility/version | RESEARCH UI; ARCHITECTURE UI | N04–N06, N08–N09 | M2-01; core/frontend versions and feature checks required. F extension hooks; our UI absent. |
| V15 | Ready usable workflows with real nodes, assets/pins, acceptance | WORKFLOW_SPEC; PLAN | N01–N28 as variant requires | M2-06, updated by M3 owners. P; no ready workflow now. |
| V16 | Versioned Project/Segment/Window/Control/Result plus analysis/recipe/binding/state | CONTRACTS 2.0.0 | N01–N28 | M1-01 sole foundation owner. P, no schemas/classes implemented. |
| V17 | Exact export frame/sample coverage, preserve/generate/mute, resumable checked outputs | CONTRACTS audio/results; WORKFLOW_SPEC | N19–N24 | M1-02/04, M2-02/05. P; media/GPU not performed. |
| V18 | Sequential model choreography, target resources, native expansion/cache risk | ARCHITECTURE resources; RESEARCH execution | N07, N09, N16–N24 | M1-04 and M2-03/05 measurements. F APIs; fit/lifetime U. |
| V19 | Outcome owners, checked common commits, <=2 initial implementing workers, separate review/GPU owner | PLAN; journal/cards; AGENTS | All ownership groups | Foundation first, actual SHA before dependencies start. Policy P; no implementation launched. |
| V20 | Docs-only verification/publication, original brief integrity, source ledger, preview/privacy | PLAN verification; RESEARCH ledger; journal | None | M0-V2V-REVISION documentation checks only; no media/code/GPU PASS. |

## Preservation and evidence boundary

Original tracked brief blob: `77e34e02374483fc19be006dc5d5b78e40f15042`; original blob SHA256: `81B86AB34ADD27455F5A6B4F37652050A5DDE0FEEB024F25616FF1D53D6C513B`. Git checkout line-ending conversion can produce a different working-file SHA; verification checks the canonical blob and preserves the pre-revision working bytes as well. No new source text, implementation, models or media is added to that brief.

All future names, schemas, inventory and wiring are proposals. Primary-source findings and unknowns belong in [RESEARCH](RESEARCH.md); acceptance belongs in [PLAN](PLAN.md) and [WORKFLOW_SPEC](WORKFLOW_SPEC.md). Detailed native session/model provenance, machine paths, auth diagnostics and private evidence stay in AO, not public documents.
