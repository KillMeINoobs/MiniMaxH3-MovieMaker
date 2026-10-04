# M2-01 — Minimal VID2VA timeline editor

- **Goal:** editable source segments/prompts that persist truthfully inside a ComfyUI workflow.
- **Scope:** approved source player/proxies/thumbnails, 24 FPS scale/cursor, add/move/delete/numeric split markers, selected segment panel, inherited/local prompt/control/seed/audio state, save/load/missing-media/relink; visible unsupported-mode drafts retained. Ordinary UI/serialization checks and docs belong to this owner.
- **Non-goals:** multitrack editor, implementing all generation modes/refs, hidden prompt rewrite, backend sampler changes, imitation run buttons, GPU concurrency.
- **Inputs/read paths:** `AGENTS.md`, brief, contracts, architecture, plan/journal; integrated M1 implementation and reviewed real sample receipt on CG; pinned JS extension docs and chosen actual frontend APIs.
- **Outputs/owned areas (proposed):** `web/` editor/state/style areas excluding runner-owned `web/run/`; UI adapter wiring to existing v1 project interfaces, corresponding UI tests/docs. Shared contracts/package/lockfiles remain foundation-owned.
- **Dependencies/base requirement:** start only after human accepts the **real M1 gate** at exact reviewed/checked **CG**. Verify receipt exists on common base; NOT PERFORMED is not an automatic substitute. Runner may parallel on CG with agreed event/area contracts. Integrate editor as CE; final combined verification includes runner outcome CR.
- **Interface version:** `KVD-WORKER/1.0.0`, schema 1.0.0; versioned editor/run events and saved project payload validated against foundation contract. Shared amendment requires new common SHA.
- **Acceptance evidence:** real browser add/move/delete/numeric markers conserve `[0,F)` exactly, adjacent distinct prompts/inheritance, stable IDs save/reload, retained inactive mode drafts, missing/changed/Unicode-path state/relink, visible prepared/canvas/output sizes; actions wired to actual runner when integrated. No large UI before GPU gate; no GPU PASS inferred from browser checks.
- **Environment/resources:** session-owned approved ComfyUI preview only after runtime authorization; no server/dependency/install changes just to display assets. Any ComfyUI/GPU use follows single named resource owner. At most two implementations with runner.
- **Publication policy:** future task assignment supplies publication scope; same owner owns UI result/tests/docs, separate AO review and owner fixes. Screenshots/media sanitized; no private source upload.
- **Status/blockers:** PROPOSED / GATED / NOT STARTED. No CG or real GPU receipt; editor functionality does not exist.

## Journal

M0: UI boundary proposed only; no JavaScript/package/server was created.
