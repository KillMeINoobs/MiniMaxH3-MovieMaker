# M2-02 — Selected runs, recovery and checked assembly

- **Goal:** reliable serial full/selected generation with durable results and explicit cancellation/retry.
- **Scope:** visible normal ComfyUI per-window queue coordination; owned prompt/request IDs; progress and atomic disk ledger; reconcile queue/history/results on reload before retry; exact selected-window cache reuse/invalidation; full/partial/passthrough export policy; connect real editor actions. Ordinary runner/integration tests/docs belong to this owner.
- **Non-goals:** recursive backend self-POST, hidden service/parallel GPU generation, global cache purges, fake results, silent source substitution, continuation/multimode expansion or modifying core.
- **Inputs/read paths:** `AGENTS.md`, brief, contracts RunSelection/status/cache/error sections, architecture/plan/journal; integrated media/adapter and real GPU receipt on CG; editor event contract and final integrated editor on CE.
- **Outputs/owned areas (proposed):** `kmin_video_director/runtime/`, `nodes/run/`, `web/run/`; corresponding runner/integration tests and run/recovery docs. Avoid concurrent edits to editor areas or common schemas/package/lockfiles.
- **Dependencies/base requirement:** start from exact integrated/reviewed/checked **CG**, interfaces present and gate accepted. May parallel editor only on agreed contract; do not assume CE code exists on CG. Before final UI/E2E checks integrate CE with runner outcome CR onto a checked common base; separate review/fixes then record full CM2.
- **Interface version:** `KVD-WORKER/1.0.0`, schema 1.0.0, owned-request event contract; validate real frontend queue/event API signatures. Shared change goes through foundation owner and updated common SHA.
- **Acceptance evidence:** one active owned window, normal queue/progress/targeted cancel, no duplicated submissions after refresh/ambiguous response, deterministic retry of failed window with prior completed results preserved, prompt edit reuses maps but invalidates generation, spatial edit invalidates maps, exact full/selected coverage/error report, missing/stale output never silently substituted; end-to-end export count/audio/dimensions. Measure repeated-window cache lifetime; if unbounded, block long-run claim and revise design. Separate CPU/mocks/media/browser/GPU evidence.
- **Environment/resources:** CPU/state work can parallel editor within <=2 policy. All real shared H3/ComfyUI validation/change sequential under one named resource owner and future authorization. No user's GPU/ports/venv/output/settings assumed by cloud/worktree.
- **Publication policy:** future assignment names commit/push/PR scope; one runner outcome with ordinary tests/docs, separate reviewer and fixes to owner. No private ledger/session/media details in public artifacts.
- **Status/blockers:** PROPOSED / GATED / NOT STARTED. CG/CE/CR/CM2 not created; actual frontend lifecycle/cache behavior needs evidence; GPU NOT PERFORMED.

## Journal

M0: run/recovery interfaces and resource rules documented; no runner or queue mutation occurred.
