# Durable task journal

This Markdown directory is our journal, **not an AO built-in scheduler**. Cards record outcomes and do not launch workers. M1 foundation is implemented as a draft; downstream outcomes remain gated. Read [direction](../PRODUCT_DIRECTION_V2V.md), [plan](../PLAN.md), [research](../RESEARCH.md), [architecture](../ARCHITECTURE.md), [contracts 2.0.0](../CONTRACTS.md), [nodes](../NODE_CATALOG.md) and [workflow specification](../WORKFLOW_SPEC.md) after the preserved brief.

## Ownership and status

| ID / card | Outcome owner | Status / next gate |
|---|---|---|
| First M0 | Original documentation outcome | Published D0, included by the accepted merged C0 |
| M0-V2V-REVISION | Research/documentation owner | Accepted merged C0; brief and source ledger preserved |
| [M1-01 foundation](M1-01-FOUNDATION.md) | Assigned foundation owner | Reviewed ac335 deployed; registration/served source PASS; selector partial; native graph/layout BLOCKED; new checker review pending; CF unaccepted |
| [M1-02 media](M1-02-MEDIA.md) | Coordinator-assigned media owner | Read-only preflight on reviewed ac335; CPU implementation after explicit release; no runtime/browser/GPU allocation |
| [M1-03 H3](M1-03-H3.md) | Adapter owner, unassigned | PROPOSED / NOT STARTED; CF start, actual CM for finish |
| [M1-04 human handoff](M1-04-GPU-GATE.md) | Future handoff owner; human generation | GATED on CH; prepare real workflow; GPU NOT PERFORMED until human evidence |
| [M2-01 editor](M2-01-EDITOR.md) | Editor owner, unassigned | PROPOSED / GATED; accepted real CG |
| [M2-02 runner](M2-02-RUNNER.md) | Runner owner, unassigned | PROPOSED / GATED; CG, final actual CE+CR |
| [M2-03 scene prompts](M2-03-SCENE-PROMPTS.md) | Scene-intelligence owner, unassigned | PROPOSED / GATED; joint CT |
| [M2-04 identity](M2-04-IDENTITY.md) | Identity owner, unassigned | PROPOSED / GATED; checked CI |
| [M2-05 continuity](M2-05-CONTINUITY.md) | Continuity owner, unassigned | PROPOSED / GATED; checked CB |
| [M2-06 workflows](M2-06-WORKFLOWS.md) | Workflow owner, unassigned | PROPOSED / GATED; checked CC, real assets/receipts |
| [M3-01 controls](M3-01-CONTROLS.md) | Controls owner, unassigned | PROPOSED / GATED; accepted CW |
| [M3-02 modes](M3-02-MODES.md) | Creation-mode owner, unassigned | PROPOSED / GATED; accepted CW |

Every outcome owner includes ordinary tests/docs. Shared schemas/package manifests/lockfiles/skeleton have one first foundation owner; consumers request amendments. Initial <=2 simultaneous IMPLEMENTING workers is project policy, not AO capacity. The coordinator assigns implementing owners and separate AO review; this journal launches none; fixes return to the owner.

GPU/H3/ComfyUI/ports/output/venv/model changes are sequential under one explicitly named allocated resource owner. Foundation retains the sole shared-ComfyUI registration/UI allocation until explicit release; generation reservation is NONE. Worktrees/Cloud do not establish GPU availability or isolation.

## Checked common commit register

| Label | Meaning | Actual full SHA / status |
|---|---|---|
| B0 | First-M0 parent/original base | 8e8cf7253862f94b7787d7065babf2878064ef82 |
| D0 | Exact task research/document base; published first M0 | 1bfcc50e204797862b2bbc014fce00e4694c122c |
| C0 | Accepted revised M0 common commit | 7960568eff779c8c35c3d28a985a243368b91c26; includes M0 final9dac703183e3e56929432054f5ebc6d63c26d8e2 |
| CF | Reviewed/checked foundation | NOT ACCEPTED; draftPR2 corrected candidate pinned through AO; live gate BLOCKED |
| M1-02 CPU interface base | Explicit source-only dependency exception | ac335b87c966b3353c5115c663d4344ff08c01a0; read-only preflight, then coordinator-released CPU work; no full CF/UI acceptance or main merge |
| CM | CF + checked media outcome | NOT CREATED |
| CH | CM + reviewed/checked adapter integration | NOT CREATED |
| CG | CH + real reviewed sample and accepted GPU decision | NOT CREATED; GPU NOT PERFORMED |
| CE / CR | Checked editor / runner outcomes | NOT CREATED |
| CT | Editor+runner actually integrated and jointly checked | NOT CREATED |
| CI | CT + accepted scene-prompt automation | NOT CREATED |
| CB | CI + accepted optional-image binding/comparison | NOT CREATED |
| CC | CB + accepted within-shot state/cut/reset evidence | NOT CREATED |
| CW | CC + real accepted ready V2V collection/workflows | NOT CREATED |
| CCTRL / CMODES | Accepted extra control / creation-mode outcomes | NOT CREATED |

No label grants authorization or guarantees files exist. Launch record requires task/owner, actual workspace/branch/HEAD, full base SHA, dependencies present and checks on that SHA, interface version, owned areas, environment/publication scope, allocated GPU owner if needed, acceptance receipts and reviewer. Integrated means on the explicitly selected shared checked branch; no automatic merge into main. Never treat an unmerged dependency's files as common-base contents.

Ordering: C0 → CF → media/adapter; adapter finish includes CM → CH → real CG → editor/runner → CT → scene prompts CI → optional identity CB → continuity CC → ready workflows CW → extra controls/modes. CPU work may parallel only on agreed checked interfaces/areas; GPU work always sequential.

## Journal policy and revision handoff

Append meaningful decisions/blockers/receipts to the relevant card, update statuses and record actual SHAs before dependencies start. No advancement by elapsed time, checkbox or upstream demo. CPU/media/browser/load/GPU evidence stays separate. Artifact reports do not imply completion. Sanitized public records use project-relative asset IDs/hashes; private media/session/native-model/auth/machine diagnostics stay in AO.

M0-V2V-REVISION: original brief preserved; explicit latest-direction supersessions, V01–V20 reconciliation, 28 proposed node roles, future non-executable workflow acceptance, contract proposal 2.0.0 and 12 outcome cards. Only documents are changed. Final checks/commit/own-branch push and compare are handed off through AO to avoid embedding a self-referential SHA. Existing PR-route blocker is not retried; no PR ownership/create/merge or main integration. That M0 outcome was documentation only; the following later assignment supersedes its launch/publication limits.

## M1-01 implementation and review checkpoint

Accepted C0 verified before edits; shared brief/ledger unchanged. One foundation owner implements actual versioned records, canonical local Project I/O, import-safe registration and four Project nodes, with scoped persisted EN/RU presentation. [Handoff](../FOUNDATION_HANDOFF.md) publishes the nine actual callable protocol signatures and typed conformance examples; no media/render handler is registered. The human's [local storage decision](../decisions/M1_LOCAL_STORAGE_SCOPE.md) replaces OS isolation claims with stable-folder/regular-file assumptions. [Validation](../validation/M1_FOUNDATION.md) distinguishes current normal-use checks from historical review findings; F2-F9 remain covered and useful F10 typed errors are retained. Draft [PR2](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2) remains draft; its exact new SHA/clean-tree receipts go through AO for separate review of the revised contract. No self-review or main merge.

The human restarted reviewed `20541f938306ff6bbf80c01565fd318ea3bcbd82`; four-class registration/schema checks passed. The dedicated UI fixture aborted loading and its old checker incorrectly logged PASS. A scoped source follow-up now waits for native graph readiness and rejects incomplete loads; synthetic-host negative/success checks pass, but updated actual EN/RU appearance/save-reload remain BLOCKED until pinned review and live verification. No deployment refresh, shared-runtime release or media/adapter launch follows from that correction. M1-04 is manual-generation handoff; workers do not enqueue/load models/infer/download weights or inspect generated user-video output. GPU NOT PERFORMED until human evidence; M2/M3 stay gated. Private assets and native/session/auth/runtime paths remain outside public artifacts.

The exact-31 review requested F12/F13 persistence and post-reload presentation
corrections. The owner corrected both checker and ordinary selector using a
shared awaited save plus status-checked server readback of only KVD.Language.
Localized saving/error/current/stored/recovery state and repeated final panel
assertions have meaningful negative/success module tests. The new checked
candidate was independently approved at ac335; its exact archive was then
deployed with unchanged backend. Actual ordinary EN/RU selector text and saved
own preference/readback/restoration were observed; other preference hashes
stayed unchanged. Complete layout/native roundtrip remains blocked. A served
wrapper discards the native load result; its exact runtime value is unrecorded.
The new owned checker captures return/stack/readiness and correlates the full
native per-call hook sequence with exact graph/panel assertions and a transient
request ID. Its 29 frontend
checks pass on synthetic hosts, including hidden-abort cases. That new source
needs pinned review before deployment; installed ac335 stays fixed. No CF or
shared-resource release follows from partial browser evidence.

The coordinator assigned a second implementer for M1-02 read-only preflight
from exact source-reviewed `ac335b87c966b3353c5115c663d4344ff08c01a0`.
CPU-only owned media/planning/assembly work follows its explicit preflight
release while UI/CF remains blocked. This is a dependency-order exception,
not a main merge or runtime/GPU grant. Foundation still owns shared contracts,
package/dependencies, frontend and central docs and is the only ComfyUI owner.
Media shared-interface changes return to foundation/coordinator; no moving or
unreviewed branch is integrated. Two implementers maximum; review stays separate.
The coordinator authorized media's checked publication as a stacked PR targeting
the foundation feature branch. Its CPU dependency remains frozen at ac335;
later UI/docs changes grant no live acceptance or unreviewed integration.
