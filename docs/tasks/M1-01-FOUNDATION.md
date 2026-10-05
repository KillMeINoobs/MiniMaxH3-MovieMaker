# M1-01 — Portable project and shared foundation

- **Goal:** A user can load/save and validate one portable project; every downstream owner has the same checked interface.
- **Scope:** Implement the proposed 2.0.0 records, validation/serialization/errors, migration policy/conformance fixtures and import-safe registration skeleton. Sole first owner for shared schemas/helpers/package metadata/dependencies/lockfiles and license/attribution decisions.
- **Non-goals:** Media decoding, H3/VLM inference, timeline UI, model download or user-environment changes.
- **Inputs/read paths:** AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/PRODUCT_DIRECTION_V2V.md, docs/RESEARCH.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/NODE_CATALOG.md, docs/WORKFLOW_SPEC.md, docs/PLAN.md, docs/tasks/INDEX.md and this card.
- **Outputs/new paths (proposed):** schemas/project.schema.json and other shared record schemas; kmin_video_director/contracts/; shared registration/version/errors; root package/dependency files and chosen lockfile; tests/contracts/, tests/imports/; contract/license documentation.
- **Dependencies/base commit:** Human-reviewed revised M0 C0; full SHA UNASSIGNED. Do not start on main or assume first M0 is integrated. Verify assigned actual C0 HEAD/read paths, implement/review/check/integrate CF and record its full SHA before dependent starts. Research/document base D0 is 1bfcc50e204797862b2bbc014fce00e4694c122c; it is not an automatic launch base.
- **Interfaces:** KVD-WORKER/2.0.0; kmin.* schema 2.0.0. Publish conformance fixtures for media/render and later draft/binding/state interfaces, with unsupported runtime features rejected.
- **Acceptance:** Stable IDs/hashes/Unicode/project-relative paths/overrides round-trip; reject absolute/traversal locators, unknown major/required features and invalid ranges/seeds/digests; explicit migration preserves original; deterministic cache defaults; project can load/save without optional Depth/Pose/VLM/enhancer/models. Shared license/notices reviewed before distribution.
- **Checks:** Future python -m pytest tests/contracts tests/imports; schema/conformance JSON parse, import with optional packages absent, public-path/privacy and git diff --check. No GPU PASS from these checks.
- **Environment:** CPU Windows-compatible environment assigned separately; no mandatory WSL. Verification dependencies may be used/installed only within future assignment scope, never inferred from M0.
- **GPU ownership:** None; do not access GPU/ComfyUI runtime. Future real consumers use one allocated sequential owner.
- **Publication/review:** NOT STARTED; this M0 does not authorize implementation/publishing. Later assignment supplies scope; one owner includes ordinary tests/docs, separate AO reviewer, fixes return to owner. No private assets/session/auth/machine diagnostics in public outputs.
- **Status/blockers:** PROPOSED / NOT STARTED; required common SHA, owner, implementation/environment/publication allocation not supplied. GPU NOT PERFORMED. Technical gates above are future blockers, not evidence of a failed run.

## Journal

First M0 established the short proof and shared-base policy. M0-V2V-REVISION reconciles this outcome with the updated product direction and proposed 2.0.0 interfaces. No code, fixture/media generation, dependency install, inference or task launch occurred.
