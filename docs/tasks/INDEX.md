# Durable task journal

This Markdown directory is our journal, **not an AO built-in scheduler**. Cards record outcomes and do not launch workers. M1 foundation is implemented as a draft; downstream outcomes remain gated. Read [direction](../PRODUCT_DIRECTION_V2V.md), [plan](../PLAN.md), [research](../RESEARCH.md), [architecture](../ARCHITECTURE.md), [contracts 2.0.0](../CONTRACTS.md), [nodes](../NODE_CATALOG.md) and [workflow specification](../WORKFLOW_SPEC.md) after the preserved brief.

## Ownership and status

| ID / card | Outcome owner | Status / next gate |
|---|---|---|
| First M0 | Original documentation outcome | Published D0, included by the accepted merged C0 |
| M0-V2V-REVISION | Research/documentation owner | Accepted merged C0; brief and source ledger preserved |
| [M1-01 foundation](M1-01-FOUNDATION.md) | Assigned foundation owner | IMPLEMENTED DRAFT / incremental review pending; live registration/UI BLOCKED, CF unaccepted |
| [M1-02 media](M1-02-MEDIA.md) | Media owner, unassigned | PROPOSED / NOT STARTED; checked CF |
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

Accepted C0 verified before edits; shared brief/ledger unchanged. One foundation owner implements actual versioned records, confined canonical Project I/O, import-safe registration and four Project nodes, with scoped persisted EN/RU presentation. [Handoff](../FOUNDATION_HANDOFF.md) publishes the nine actual callable protocol signatures and typed conformance examples; no media/render handler is registered. [Validation](../validation/M1_FOUNDATION.md) records CPU/Windows race/presentation receipts and owner fixes for independent review F1-F9. Draft [PR2](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2) remains draft; its corrected full SHA and clean-tree receipts are reported through AO before an incremental separate review. No self-review or main merge.

Live node registration/frontend/EN-RU appearance/save-reload remain BLOCKED pending a human-supported Desktop restart of the reviewed snapshot. No shared-runtime release and no media/adapter launches yet. M1-04 is manual-generation handoff; workers do not enqueue/load models/infer/download weights or inspect generated user-video output. GPU NOT PERFORMED until human evidence; M2/M3 stay gated. Private assets and native/session/auth/runtime paths remain outside public artifacts.
