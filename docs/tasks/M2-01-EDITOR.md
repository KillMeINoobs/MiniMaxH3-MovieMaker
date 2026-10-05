# M2-01 — Editable scenes and persistent timeline

- **Goal:** A user edits scene boundaries and per-scene prompts, then restores that state from a ComfyUI workflow.
- **Scope:** Player/proxies/scale/cursor; add/move/delete/numeric editorial markers; separate technical-window overlay; selected scene inheritance/local prompts/control/seed/audio; project workflow persistence/missing-asset relink. Own ordinary UI tests/docs.
- **Non-goals:** Full multitrack editor, VLM/detection/identity/state backend, core patches, fake run buttons or GPU concurrency.
- **Inputs/read paths:** AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/PRODUCT_DIRECTION_V2V.md, docs/RESEARCH.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/NODE_CATALOG.md, docs/WORKFLOW_SPEC.md, docs/PLAN.md, docs/tasks/INDEX.md and this card.
- **Outputs/new paths (proposed):** web/editor/, nodes/editor/; tests/editor/; docs/workflows/EDITOR.md. Agreed shared editor/run events consumed from foundation; web/run belongs to runner.
- **Dependencies/base commit:** Accepted real M1 CG with exact reviewed/checked SHA and receipt. May parallel runner on agreed disjoint event/area contract. Editor integration CE; final actual joint CT includes checked CR, not presumed runner files. Research/document base D0 is 1bfcc50e204797862b2bbc014fce00e4694c122c; it is not an automatic launch base.
- **Interfaces:** KVD-WORKER/2.0.0 Project/Segment/PromptRecipe drafts and versioned events. Frozen accepted state differs from new drafts; technical windows never become editorial records.
- **Acceptance:** Real browser player/markers/numeric edits conserve [0,F); adjacent distinct prompts/inheritance/IDs survive save/reload; missing/changed/Unicode assets relink; window overlay distinct; actual canvas/output sizes and unsupported mode drafts visible. Runner actions are genuinely wired for final CT checks.
- **Checks:** Future python -m pytest tests/editor for serialization/events plus actual browser interaction/save/reload/missing-file checks on selected core/frontend pair; git diff --check. Browser alone is not H3 PASS.
- **Environment:** Authorized session-owned ComfyUI preview; actual frontend version/hooks checked, DaSiWa visual ideas only. No server/dependencies just for static docs; no assumed user ComfyUI access.
- **GPU ownership:** CPU/UI by default; real shared ComfyUI/H3 interactions sequential under named allocated owner. Target resources not assumed from worktree.
- **Publication/review:** NOT STARTED; this M0 does not authorize implementation/publishing. Later assignment supplies scope; one owner includes ordinary tests/docs, separate AO reviewer, fixes return to owner. No private assets/session/auth/machine diagnostics in public outputs.
- **Status/blockers:** PROPOSED / NOT STARTED; required common SHA, owner, implementation/environment/publication allocation not supplied. GPU NOT PERFORMED. Technical gates above are future blockers, not evidence of a failed run.

## Journal

First M0 established the short proof and shared-base policy. M0-V2V-REVISION reconciles this outcome with the updated product direction and proposed 2.0.0 interfaces. No code, fixture/media generation, dependency install, inference or task launch occurred.
