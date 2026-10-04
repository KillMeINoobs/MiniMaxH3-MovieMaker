# M2-02 — Bounded selected runs, recovery and export

- **Goal:** A user generates selected/all scenes serially, resumes/retries safely and exports checked coverage.
- **Scope:** Visible ordinary per-window queue coordination; frozen requests/owned prompt IDs, durable atomic receipts, cancel/retry/refresh recovery, cache/quotas and selected/full assembly. Connect editor run/review actions; own ordinary tests/docs.
- **Non-goals:** Recursive backend self-POST, hidden global service/unlimited loop, parallel GPU, global cache purge, silent source substitution, continuation or alternate modes.
- **Inputs/read paths:** AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/PRODUCT_DIRECTION_V2V.md, docs/RESEARCH.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/NODE_CATALOG.md, docs/WORKFLOW_SPEC.md, docs/PLAN.md, docs/tasks/INDEX.md and this card.
- **Outputs/new paths (proposed):** kmin_video_director/runtime/, nodes/run/, web/run/; tests/runtime/; docs/workflows/RUNNING.md. Editor areas/shared schema/package metadata remain other owners'.
- **Dependencies/base commit:** Start actual CG, may parallel editor on agreed interfaces. CR + integrated CE are checked together as CT before final UI/E2E acceptance; assignment/journal records real common SHAs. Research/document base D0 is 1bfcc50e204797862b2bbc014fce00e4694c122c; it is not an automatic launch base.
- **Interfaces:** RunSelection/RenderResult/AssembleExport and owned events, KVD-WORKER/2.0.0. State-chain hooks reserved for later tested capability.
- **Acceptance:** One active H3 window; targeted owned cancel retains completed receipts; ambiguous submission/reload reconciled before retry; deterministic failed/stale rerun without duplicate good windows; prompt edit reuses maps; missing output blocks full export; actual frame/sample/geometry counts. Long input bounded by measured RAM/VRAM and disk quota; browser closure stops new submissions after active run.
- **Checks:** Future python -m pytest tests/runtime; fault/reload/ambiguous-response/cancel/cache tests, actual browser selection/export and authorized repeated-window peak/lifetime receipts. If memory grows, BLOCKED long-run acceptance and revise lifetime design.
- **Environment:** CPU/state logic on assigned base; actual frontend queue/history/event signatures checked. Future runtime access only within allocated scope; no implicit installs/models/user settings.
- **GPU ownership:** Actual H3 and shared ComfyUI checks sequential under one allocated owner; worktree/Cloud is not GPU isolation.
- **Publication/review:** NOT STARTED; this M0 does not authorize implementation/publishing. Later assignment supplies scope; one owner includes ordinary tests/docs, separate AO reviewer, fixes return to owner. No private assets/session/auth/machine diagnostics in public outputs.
- **Status/blockers:** PROPOSED / NOT STARTED; required common SHA, owner, implementation/environment/publication allocation not supplied. GPU NOT PERFORMED. Technical gates above are future blockers, not evidence of a failed run.

## Journal

First M0 established the short proof and shared-base policy. M0-V2V-REVISION reconciles this outcome with the updated product direction and proposed 2.0.0 interfaces. No code, fixture/media generation, dependency install, inference or task launch occurred.
