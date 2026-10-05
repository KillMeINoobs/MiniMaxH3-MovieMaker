# M3-02 — Native video-creation modes

- **Goal:** A user creates video with tested text, image/keyframe and full-reference modes alongside the main V2V product.
- **Scope:** Real native T2VA/I2VA/FL2VA/L2VA/Ref2VA routes, mode-specific visible prompts/references and saved drafts; validate video/audio refs if included, update workflow/setup/capability matrix. Own ordinary tests/docs.
- **Non-goals:** V2V redesign, hosted Context-IR/2K equivalence, universal third-party extension support, training/refinement or fake toggles.
- **Inputs/read paths:** AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/PRODUCT_DIRECTION_V2V.md, docs/RESEARCH.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/NODE_CATALOG.md, docs/WORKFLOW_SPEC.md, docs/PLAN.md, docs/tasks/INDEX.md and this card.
- **Outputs/new paths (proposed):** kmin_video_director/modes/, nodes/modes/, web/modes/; tests/modes/; workflows/create_video_modes.json; docs/validation/M3_MODES.md. Shared schemas/dependencies through foundation.
- **Dependencies/base commit:** Actual checked CW, full assigned SHA. Preserve accepted V2V/no-ref behavior; integrate/check CMODES; shared release combines reviewed control/mode commits only after both actually exist. Research/document base D0 is 1bfcc50e204797862b2bbc014fce00e4694c122c; it is not an automatic launch base.
- **Interfaces:** KVD-WORKER/2.0.0 plus independent canonical mode guide versions/native model-family schemas. FL2VA vs Ref2VA and explicit keyframes/reference roles remain separate.
- **Acceptance:** Actual tested mode paths/keyframe anchors, visible final text/labels, supported card quotas/time bounds and saved inactive drafts; useful count/audio/export strict caps; V2V remains first/main. Any untested mode disabled with explanation; ready workflow word requires WORKFLOW_SPEC acceptance.
- **Checks:** Future python -m pytest tests/modes; mode/refs serialization and graph fixtures; actual keyframe/full-reference/text GPU runs and workflow import/export, with separate receipts and no implicit source appearance route.
- **Environment:** Approved compatible existing components/assets and explicit later scope for video/audio references. No paid hosted API or mandatory WSL; exact license/conversion/runtime pins.
- **GPU ownership:** One allocated sequential owner for all mode/H3/shared-ComfyUI checks; workflow updates sequenced with controls owner.
- **Publication/review:** NOT STARTED; this M0 does not authorize implementation/publishing. Later assignment supplies scope; one owner includes ordinary tests/docs, separate AO reviewer, fixes return to owner. No private assets/session/auth/machine diagnostics in public outputs.
- **Status/blockers:** PROPOSED / NOT STARTED; required common SHA, owner, implementation/environment/publication allocation not supplied. GPU NOT PERFORMED. Technical gates above are future blockers, not evidence of a failed run.

## Journal

First M0 established the short proof and shared-base policy. M0-V2V-REVISION adds this outcome for the updated product direction and proposed 2.0.0 interfaces. No code, fixture/media generation, dependency install, inference or task launch occurred.
