# V2V-first staged product plan

**M1-01 source/CPU approved at `ac335b8`; four-class registration/served source PASS. Ordinary selector has partial browser evidence; native graph/layout gate remains BLOCKED. A new checker candidate needs pinned review; CF remains unaccepted. GPU NOT PERFORMED.** Follow the [preserved brief](PROJECT_BRIEF.md) and [superseding direction](PRODUCT_DIRECTION_V2V.md), [research](RESEARCH.md), [architecture](ARCHITECTURE.md), [contracts 2.0.0](CONTRACTS.md), [proposed nodes](NODE_CATALOG.md), [future workflow acceptance](WORKFLOW_SPEC.md) and [journal/cards](tasks/INDEX.md). Four Project nodes and shared contracts now exist; media/H3/editor operations remain future work. See [the actual handoff](FOUNDATION_HANDOFF.md), [execution scope](decisions/M1_EXECUTION_SCOPE.md) and [validation](validation/M1_FOUNDATION.md).

Goal: a complete usable ComfyUI video node collection, built around gameplay/low-poly → cinematic V2V. Prove a short no-ref Canny/native-H3 path first. Then deliver scenes and reliable long-input execution, editable analyzed/enhanced prompts, optional image identity, measured continuation/cut resets, and real workflows. Additional controls and creation modes extend that product.

## Bases and checked common commits

Exact document revision base **D0**: 1bfcc50e204797862b2bbc014fce00e4694c122c (first M0, not merged into main). Parent **B0**: 8e8cf7253862f94b7787d7065babf2878064ef82. This revision advances only its assigned branch from B0 to D0 before editing; it does not integrate main. Neither main nor an unreviewed documentation branch is an automatic implementation launch base.

Accepted **C0** is `7960568eff779c8c35c3d28a985a243368b91c26`, the actual merged documentation base containing M0 head `9dac703183e3e56929432054f5ebc6d63c26d8e2`. Foundation starts from C0. CF remains unaccepted; the corrected candidate is pinned through AO/draft PR2 for incremental independent review. A checked common commit may live on an explicitly selected shared integration branch; no main merge is implied. Each dependent verifies the actual full SHA, required interfaces/files and checks there. Symbolic labels and presumed unmerged files are insufficient.

The coordinator explicitly assigned M1-02 read-only preflight on source-reviewed
`ac335b87c966b3353c5115c663d4344ff08c01a0`; its CPU-only implementation follows
the separate preflight release while full UI/CF acceptance remains blocked.
This ordering exception grants no ComfyUI/browser/deployment/GPU allocation.
Foundation keeps sole shared-file/runtime ownership; interface changes return
to that owner, and downstream integration still requires checked assigned SHAs.

~~~mermaid
flowchart TD
  C0[Accepted checked revised M0 C0] --> F[M1-01 portable foundation]
  F --> CF[Checked common CF]
  CF --> M[M1-02 real CFR24 media and plan]
  CF --> H[M1-03 Canny and native adapter]
  M --> CM[Checked media CM]
  CM --> HI[M1-03 integration on CM]
  H --> HI
  HI --> CH[Checked integrated M1 CH]
  CH --> G[M1-04 workflow handoff for human generation]
  G --> CG[Human evidence and reviewed GPU decision CG]
  CG --> E[M2-01 editable scene timeline]
  CG --> R[M2-02 bounded runs and recovery]
  E --> CT[Both outcomes checked together CT]
  R --> CT
  CT --> I[M2-03 editable scene intelligence]
  I --> CI[Checked prompt gate CI]
  CI --> B[M2-04 optional subject image identity]
  B --> CB[Checked identity gate CB]
  CB --> K[M2-05 continuation and cut resets]
  K --> CC[Checked continuity gate CC]
  CC --> W[M2-06 real ready V2V workflows]
  W --> CW[Accepted V2V release CW]
  CW --> C[M3-01 controls and mixed decision]
  CW --> V[M3-02 native creation modes]
~~~

- **One first foundation owner** controls shared schemas/errors, package metadata/dependencies/lockfiles, skeleton and conformance fixtures. Downstream starts after reviewed/checked integration CF. Amendments return to that owner and yield a new actual common SHA.
- Initial project policy: **at most two simultaneous IMPLEMENTING workers**, not an AO platform limit. Media/adapter may start on CF; adapter finishes on a common commit containing CM. Editor/runner may start on CG in separate areas/event contracts; joint acceptance uses integrated CT.
- Explicit central gates are CI (prompt automation), CB (identity), CC (continuity), CW (ready workflows). These are product priorities, not generic M3 nice-to-haves. Optional features preserve manual/no-ref operation, but advertised variants need real supported-backend receipts.
- Future code review uses a **separate AO reviewer**; fixes return to the outcome owner. The coordinator assigns independent review; this journal does not launch sessions.
- GPU/H3/shared-ComfyUI work is sequential under one named allocated resource owner. Worktrees do not isolate GPU, venv, ports, output or model settings. Foundation alone holds shared-ComfyUI registration/UI ownership until explicit release. Generation reservation is NONE; no worker inference is authorized.
- GPU NOT PERFORMED is an honest unexecuted/blocked gate, not PASS. If a real M1 sample is unavailable, report it before any large timeline and return the gate/scope decision to the human; M2 does not open automatically.

## Outcome backlog

Each card owns one user-visible result plus ordinary tests/docs. Shared metadata/schemas remain foundation-owned; use the actual foundation handoff for implemented shared interfaces; downstream nodes remain proposals.

| Card | User-visible outcome | Starting/final common commit | Node groups |
|---|---|---|---|
| [M1-01 foundation](tasks/M1-01-FOUNDATION.md) | Load/save and validate portable projects without optional models | C0 → CF | N01; shared records/interfaces |
| [M1-02 media](tasks/M1-02-MEDIA.md) | Add source → measured CFR24, legal plan, accurate CPU export | CF → CM | N02/N03/N10/N12/N23 |
| [M1-03 H3](tasks/M1-03-H3.md) | Canny preview and checked bounded native H3 path; refs not forced | CF; final CM → CH | Manual N11; N13/N15/N16/N20/N26 |
| [M1-04 human handoff](tasks/M1-04-GPU-GATE.md) | Loadable workflow/manual run instructions; human supplies controlled/off evidence | CH → CG after review/decision | N24 + M1 path |
| [M2-01 editor](tasks/M2-01-EDITOR.md) | Editable scene/local prompts and workflow persistence | CG → CE; joint CT | N04/N06/N25 |
| [M2-02 runner](tasks/M2-02-RUNNER.md) | Serial selected/full runs, recovery/retry and export without holes | CG → CR; CE+CR → CT | N21/N22; N23/N24 integration |
| [M2-03 scene prompts](tasks/M2-03-SCENE-PROMPTS.md) | Review cut proposals and bounded VLM/enhancer prompt drafts | CT → CI | N05/N07/N09; structured N11 |
| [M2-04 identity](tasks/M2-04-IDENTITY.md) | Optional appearance images bind subjects across scenes | CI → CB | N08; reference N11/N15 |
| [M2-05 continuity](tasks/M2-05-CONTINUITY.md) | Continue a shot, reset at cuts and resume compatible state | CB → CC | N17–N19; context N10/N20/N22 |
| [M2-06 workflows](tasks/M2-06-WORKFLOWS.md) | Actual supplied usable V2V workflows and setup/receipts | CC → CW | N28 + accepted V2V collection |
| [M3-01 controls](tasks/M3-01-CONTROLS.md) | Validated Depth/Pose/Gray and evidence-based mixed decision | CW → CCTRL | N14/N26; updated workflow |
| [M3-02 modes](tasks/M3-02-MODES.md) | Tested native text/keyframe/full-reference creation modes | CW → CMODES | N27/N28; updated workflow |

M3 controls/modes can share a base with disjoint areas; GPU validation and shared workflow changes stay sequential. Record their checked combined release. Unsupported mixed controls stay disabled with an explicit evidence-based reason.

## M1 shortest verified path

1. Accept revised M0, record C0 and assign foundation/publication scope. Implement/check shared 2.0.0 records and optional-import-safe skeleton; separately review/integrate CF. The explicit ac335 CPU-only M1-02 exception above does not satisfy the outstanding live UI gate.
2. Media produces actual timestamp normalization, canonical disk artifacts, balanced no-context windows, spatial transforms and absolute audio accounting. Adapter works against CF conformance fixtures, knowing real media code is absent there.
3. Integrate CM; finish adapter on that actual common commit. Expand normal native nodes, exact Canny maps, frozen visible prompt/seed/profile and useful finalization. Source RGB/audio ref, guide and inpaint inputs are absent; refs/context empty. Review/check CH.
4. Prepare a real, registered workflow for the human with the approved existing runtime/models. Workers do not enqueue, load models or perform inference. Template converted Ref2VA + original Union is first recipe. A deliberate v2 profile needs ten-block/AdaLN/post_norm/conversion validation, not filename substitution. No implicit installs/downloads/ComfyUI changes.
5. The human may run a short clip with source audio preserved if present and a same-setting control-off, then provide evidence. Check actual CFR24/counts/geometry/audio, timings and memory. Include F=360 two-window assembly, repeated-window lifetime and cancellation. Retain local receipts and honest human judgment of Canny benefit/photorealism limits.
6. Review human-supplied evidence independently of CPU/mocks before the human accepts CG. Workers do not inspect generated user-video output under this assignment. Missing resources produce GPU NOT PERFORMED and the exact blocker; no fit claim or automatic large editor launch.

## Central V2V product gates

**CT timeline/runner:** manual scenes/prompts, exact coverage/persistence, bounded owned queue requests and durable recovery. Detection proposals and window edges are separate layers. Browser closure stops new submissions after the active owned window; reconcile before resume/retry.

**CI scene prompts:** streamed detector proposals/manual correction; actual supported Qwen VLM with bounded frame/time/token coverage; editable observations and independent text-enhancer adapter. Validate three/six-block recipes, dialogue locks, manifest/guide versions and local window timing; test missing optional backend/manual fallback and scoped teardown before H3. Source and desired output styles are separate. A string-only enhancer or embedded H3 encoder cannot replace the VLM.

**CB identity:** optional images/stable subjects and real local labels/sockets. Compare two scenes with no-ref / bound-ref / cleared or reordered refs on a matched native Fun profile. Assess identity across a cut, recording limits. Never route raw source RGB to appearance/inpaint automatically.

**CC continuity:** actual native Fun + refs + Motion-Context combination. Compatible same-shot windows carry bounded state; cuts/profile/geometry changes reset it. C+U+padding<=345 on the lattice; maps align to predecessor history. First head profile explicitly makes audio follow video and maps audio-grid overhang instead of inheriting a longer independent audio window. Padded latent tails need a verified mapping or explicit decoded-tail/replanned fallback. One trim and absolute audio fitting; predecessor edits invalidate successors to reset, independently from identity.

**CW ready workflows:** real UI/API assets with registered nodes, exact required/optional dependencies and model profiles, relink/setup/manual/no-ref variants and actual Windows load/run/resource/recovery/identity/continuity receipts. Illustrative JSON/proposed nodes cannot satisfy ready. [WORKFLOW_SPEC](WORKFLOW_SPEC.md) governs acceptance.

## Future checks and acceptance

Everything in this table is future acceptance, not results. Record CPU/logic, synthetic media, browser, load/preflight and GPU separately as PASS/FAIL/BLOCKED/NOT PERFORMED; queue events alone are not success.

| Case | Required evidence / gate |
|---|---|
| Tiny clip / short tail | L=1 pads to N=124; L=346 → 173/173 useful, N=175, exact coverage. Real padded sample checks quality; shape minimum alone cannot. M1-02/04. |
| Sub-frame source span | D=1/120 s → rounded R=0 → minimum F=1 → duration error=1/30 s, with applied duration-clamp provenance. Ordinary D>=1/48 rounding error <=1/48 s; clamped 0<D<1/48 error <1/24 s. Document/formula boundary checks below; real decoded-media acceptance remains future M1-02. |
| Exactly 15 s | F=360 → 180+180 useful, N=192 each, 12 pad each; export 360. Never submit 362/discard to 345. Real M1-04 assembly. |
| Continuation cap | Useful capacity <=345-C, all overhead in N. Proposed C=22/F=360 plan 192 then 168 useful, N=192 each; no runtime claim. M2-05. |
| Long input | Streamed disk media; F=1000 no-context 334/333/333/N=345; quotas, multiple-window measured plateau/recovery. CPU planning is not long GPU evidence. M1-02/M2-02. |
| Fractional/VFR | 23.976/29.97/30/60/VFR PTS/drop/duplicate receipts; preserved speed, 24/1 increments, EOF/discontinuity policy explicit. |
| Geometry | 4:3/portrait/rotation/SAR/off-grid; 640x360 → canvas 640x384 → 640x360; same coordinates for RGB/maps/masks/results; odd-codec limits visible. |
| Audio | +/- offsets, boundary/end impulses, absolute Q, continuous PCM, one encode and measured codec delay. Preserve/mute/no audio distinct from generated audio and refs; no accumulating shift. |
| Files/state | Project-relative IDs/hashes/paths, spaces/Cyrillic, save/relink/stable IDs/overrides/version rejection; no guessed assets. |
| Control/no refs | Actual same-settings on/off except patch; empty appearance/guide/inpaint sockets; Canny/source preview. M1-03/04. |
| Scenes | Add/move/delete/numeric markers and distinct prompts; cut accept/reject/adjust, false cuts/fades/HUD cases; independent window overlay. M2-01/03. |
| Analysis/prompts | All scene chunks covered with max gaps/uncertainties and resampling; real VLM backend, accepted visible text, no invented dialogue/no-clobber edits. M2-03. |
| Images | Socket/label agreement, presence across scenes, clearing/reorder/relink and no-ref regression; actual combined profile/quality/resource report. M2-04. |
| Continuation | Same-shot/cut/profile/padded-tail cases; combined profile, one trim/global samples, compatible restart and honest seams/drift. M2-05. |
| Recovery/cache | Owned cancellation, prior receipts retained, ambiguous requests reconciled, prompt edit reuses maps, predecessor invalidation stops at reset. M2-02/05. |
| Workflow usability | Actual import/no fake nodes, setup/relink, optional-dependency absence, manual path, budgets and full receipts. M2-06; M3 updates. |

Video: export exactly F useful frames, PTS 1/24, declared dimensions, no duplicate head/pad, canonical-source duration error <=1 frame without accumulation. PCM slice counts use global Q exactly, rounding <=1 output sample, codec presentation delay separately measured, no growing offset. Generated-audio corrections/seams are reported.

Normalization compares F/24 with the decoded source span D: error <=1/48 s when D>=1/48 s; the minimum-one-frame case 0<D<1/48 s records its clamp and error <1/24 s. Exactly F CFR frames and the <=1-frame export acceptance remain required; the bounds do not permit per-window duration errors to accumulate.

## Environment, publication and review

Current M1 assignment authorizes own feature commits/SSH push, one draft PR, isolated CPU verification and reviewed own-package snapshots for registration/UI checks. No main merge. Human-restarted205 registered; reviewed ac335 was refreshed from its exact archive with unchanged backend and served-source proof. The new checker compatibility/diagnostic correction requires pinned review before deployment. No further restart, lifecycle workaround, second server, shared-venv/core/other-pack change, generation or weights are authorized at this follow-up stage. CF remains gated by independent review and actual live evidence.

The following M0 publication record is historical:

This M0 permits docs edits/checks, local doc commit and **own assigned-branch push using existing origin SSH**, with commit/compare handoff. No PR claim/create/merge, auth/config changes, M1/M2 launch, installs/weights/paid calls/uploads/inference or user ComfyUI changes. A recorded publication-route blocker is reported privately in AO and not retried. Main/other worktrees and branches remain untouched.

Future assignments identify full checked SHA, owner/interfaces, dependencies actually present, approved media/runtime/model availability, publication scope/checks/reviewer and one sequential GPU owner when applicable. Public evidence is sanitized; private native-session/auth/machine diagnostics stay in AO. Reviewer does not take ownership; owners fix/recheck. docs/tasks is a journal, not AO scheduling.

## Document verification

M0 checks only documentation: owned paths/cards, V01–V20 reconciliation, source pins/evidence levels, local file/anchor links, illustrative JSON parsing (partial records are not implemented schemas), coherent 2.0.0 records/common-commit ordering, docs-only diff, git diff --check, unchanged brief canonical blob/SHA and pre-edit checkout bytes, and no public private-session/machine/auth diagnostics. Preview primary docs/PLAN.md using existing AO static preview, with no new server/dependency/launch configuration.

Original brief blob: 77e34e02374483fc19be006dc5d5b78e40f15042; canonical SHA256: 81B86AB34ADD27455F5A6B4F37652050A5DDE0FEEB024F25616FF1D53D6C513B. Check canonical Git and checkout bytes separately because line-ending conversion differs. Fresh check results/counts and final commit/branch are supplied after verification; no code/media/GPU PASS follows from them.

**Document-check receipt, 2026-10-05 Europe/Moscow:** 23 Markdown files inspected; 87 local file/anchor links resolved; 31 table column structures checked; six illustrative JSON records parsed with coherent proposed versions/intervals. Reconciliation contains V01–V20, N01–N28, 24 source-ledger entries and 12 complete outcome cards with required read paths/interfaces/base/dependency gates. Integer calculations checked the four no-context length examples, the proposed 22-frame continuation example and 12 absolute-audio-boundary cases; these are document/formula checks, not implementation or media tests.

**Document-review follow-up:** exact rational calculations checked five source-duration cases: D=1/120 s, D=1/48 s minus/plus 1/48000 s, D=1/48 s exactly, and D=1/24 s. The short-span case gives R=0, F=1, duration_error=1/30 s, confirming that the old unconditional <=1/48 s statement was incorrect. Below the threshold the clamp is applied and error <1/24 s; at/above it ordinary error <=1/48 s holds. CONTRACTS and M1-02 now require explicit duration-clamp provenance while preserving exact F and <=1-frame export acceptance. These are documentation/formula checks only; no implementation test or media execution occurred. Source pins and other research conclusions are unchanged.

The 22 changed paths are documentation only; staged `git diff --check` passed. Original brief canonical blob/SHA and pre-edit checkout bytes match. Public path/privacy and stale-interface scans passed, with a manual scope/evidence/common-commit review. AO static preview of this PLAN was inspected: eight headings and two tables are present, browser errors are empty; Mermaid is displayed as a source block in that preview. The final commit/push receipt is supplied in AO and the handoff. **This was the M0 documentation receipt: no code/media/model/GPU verification was performed then.**

## M1-01 checkpoint, 2026-10-05

Foundation owns shared schemas/contracts/registration/errors/version/dependencies and UI settings/translations. Actual schema 2.0.0 records, canonical portable Project I/O, four Project nodes and nine callable downstream protocols exist. The human narrowed storage to ordinary stable local folders in the [local storage decision](decisions/M1_LOCAL_STORAGE_SCOPE.md), superseding OS isolation claims after the fdce review. Independent source/CPU review approved `20541f938306ff6bbf80c01565fd318ea3bcbd82` under that contract. Its human-restarted snapshot registered all four classes. The opt-in UI fixture hit a loading error and falsely logged PASS, so appearance/persisted language/workflow reload remain BLOCKED. The scoped checker correction has negative and successful synthetic-host tests; its new exact candidate needs separate review and actual browser evidence. See [M1 foundation validation](validation/M1_FOUNDATION.md). GPU/video NOT PERFORMED; no CF acceptance, resource release or downstream launch. M1-04 is manual-generation handoff, M2/M3 remain gated.

Exact-31 review then found unverified setting persistence/restoration and missing
final panels (F12/F13). The owner follow-up includes the ordinary language
selector, a shared awaited save/readback helper and localized honest failure
state, plus repeated graph/panel checks. These source/CPU corrections require
a new pinned review; installed205 stayed fixed during that source stage.
Independent review then approved ac335, whose exact archive was refreshed with
unchanged backend and verified served assets/registration. Actual ordinary
selector/readback/restoration has partial browser evidence. Complete native
graph/layout is still blocked; the new lifecycle/diagnostic checker has
29 synthetic frontend checks and needs pinned review before deployment.
The coordinator assigned M1-02 read-only preflight from exact reviewed ac335,
with CPU work after explicit preflight release and checked stacked publication
targeting foundation. This grants no shared runtime/UI/CF acceptance or main
merge; foundation retains shared-file/runtime ownership.
