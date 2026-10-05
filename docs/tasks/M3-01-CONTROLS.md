# M3-01 — Additional structural choices and mixed-control decision

- **Goal:** A user selects validated Depth/Pose/Gray and sees a truthful supported/unsupported decision for requested mixed pairs.
- **Scope:** Optional temporal preprocessors/calibration, matched Union profiles, single-control real comparisons and explicit Canny+Depth/Depth+Pose representation/backend investigation. Enable mixed only with source-supported encoding and measured combination; update controls workflow/docs.
- **Non-goals:** Declaring support by arithmetic blending/patch stacking, silent v1/v2 substitution, compulsory preprocessors, training or unlimited resource promises.
- **Inputs/read paths:** AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/PRODUCT_DIRECTION_V2V.md, docs/RESEARCH.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/NODE_CATALOG.md, docs/WORKFLOW_SPEC.md, docs/PLAN.md, docs/tasks/INDEX.md and this card.
- **Outputs/new paths (proposed):** kmin_video_director/controls/additional/, adapters/control_profiles/; tests/controls/; workflows/v2v_controls.json; docs/validation/M3_CONTROLS.md. Shared metadata via foundation; workflow changes sequential after CW.
- **Dependencies/base commit:** Actual checked CW; full assigned SHA and accepted V2V regressions. Integrate/check CCTRL; do not assume another concurrent modes branch is present. Research/document base D0 is 1bfcc50e204797862b2bbc014fce00e4694c122c; it is not an automatic launch base.
- **Interfaces:** ControlSpec components/representation_id and strict profiles, KVD-WORKER/2.0.0. Unknown mixed capability stays disabled; record explicit rejection/unknown rather than fake map support.
- **Acceptance:** Temporal Depth normalization and Pose/Gray representation match native IMAGE geometry/time; compatible checkpoint/kernel/metadata tested; no-ref regression; real single comparisons and resource receipts. Mixed decision cites actual trained/backend representation or states absent evidence and remains disabled. No input-role/appearance leakage.
- **Checks:** Future python -m pytest tests/controls; optional-import absence, calibration/geometry/count fixtures, real single-control GPU comparisons and any supported mixed experiment. Document unknown/failed cases honestly.
- **Environment:** Approved existing optional extractor/model/runtime; exact package/model licenses and revisions. No automatic first-run weights/install; target fit unverified until this profile measured.
- **GPU ownership:** One allocated sequential owner for extractor/H3/shared-ComfyUI runs; shared workflow asset updates coordinated with mode outcome.
- **Publication/review:** NOT STARTED; this M0 does not authorize implementation/publishing. Later assignment supplies scope; one owner includes ordinary tests/docs, separate AO reviewer, fixes return to owner. No private assets/session/auth/machine diagnostics in public outputs.
- **Status/blockers:** PROPOSED / NOT STARTED; required common SHA, owner, implementation/environment/publication allocation not supplied. GPU NOT PERFORMED. Technical gates above are future blockers, not evidence of a failed run.

## Journal

First M0 established the short proof and shared-base policy. M0-V2V-REVISION adds this outcome for the updated product direction and proposed 2.0.0 interfaces. No code, fixture/media generation, dependency install, inference or task launch occurred.
