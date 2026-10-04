# M1-01 — Shared contract and package foundation

- **Goal:** one checked common foundation for every downstream owner.
- **Scope:** implement versioned serialization/validation/error types and interface conformance examples; minimal ComfyUI registration/import skeleton; shared version/cache-key helpers; dependency tooling and project license/borrowing decisions. One first owner controls all schemas, manifests, lockfiles and shared skeleton.
- **Non-goals:** media pipeline, H3 inference, timeline editor, model download, environment modification, exhaustive multimode support.
- **Inputs/read paths:** `AGENTS.md`, `README.md`, `docs/PROJECT_BRIEF.md`, `docs/RESEARCH.md`, `docs/ARCHITECTURE.md`, `docs/CONTRACTS.md`, `docs/PLAN.md`, this card and `docs/tasks/INDEX.md`.
- **Outputs/owned areas (proposed):** `schemas/`, `kmin_video_director/contracts/`, shared version/error helpers, root registration/package/dependency files and any chosen lockfile, foundational tests/conformance fixtures, updated contract/license docs. Other owners request changes here rather than edit shared files concurrently.
- **Dependencies/base requirement:** human accepts M0 and records exact integrated C0. Start only from that checked SHA, verifying actual HEAD and doc contents. Publish/review/integrate the outcome as CF and record full SHA before any downstream start.
- **Interface version:** `KVD-WORKER/1.0.0`, `kmin.*` schema 1.0.0; approve any amendment in docs first and give consumers the revised common SHA.
- **Acceptance evidence:** round-trip stable IDs/Unicode/overrides; reject unknown major/required capability; invalid ranges/seed/digests explicit; migration preserves originals; cache keys deterministic with effective defaults; import without Depth/Pose/model weights; package/shared metadata reviewed. Tests and docs belong to this owner. These checks are not H3 evidence.
- **Environment/resources:** CPU Windows-compatible implementation; no mandatory WSL. Dependency installation for verification requires assignment scope; do not modify the user's working ComfyUI/venv. No GPU or port ownership.
- **Publication policy:** NOT AUTHORIZED by M0 backlog; future assignment must name commit/push/PR scope. Prefer one outcome PR with tests/docs after permission applies. No personal data/weights. Separate AO reviewer; fixes return to owner.
- **Status/blockers:** PROPOSED / NOT STARTED. Blocked on human M0 decision, exact C0, named owner and implementation/publication authorization; license choice/borrowed-code attribution must be resolved before distribution.

## Journal

M0: card authored; no code, package/lockfile or task launch exists.
