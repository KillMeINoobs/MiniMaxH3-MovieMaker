# M2-04 — Optional image identity across scenes

- **Goal:** A user maps a subject to a photorealistic image reference across scenes and can clear it to retain structural-only V2V.
- **Scope:** Image library/stable subjects/presence/appearance bindings, project-relative hashes, actual local socket/label manifests, enhancer translation and native combined-profile evidence. Own ordinary tests/docs and identity comparison.
- **Non-goals:** Mandatory image refs, raw-source automatic appearance/inpaint, face swap, recognition guarantees, arbitrary video/audio refs or AV continuation.
- **Inputs/read paths:** AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/PRODUCT_DIRECTION_V2V.md, docs/RESEARCH.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/NODE_CATALOG.md, docs/WORKFLOW_SPEC.md, docs/PLAN.md, docs/tasks/INDEX.md and this card.
- **Outputs/new paths (proposed):** kmin_video_director/references/, adapters/reference_binding/, web/references/; tests/references/; docs/validation/M2_IDENTITY.md. Foundation handles shared-schema amendments; native adapter consumes tested bindings.
- **Dependencies/base commit:** Actual reviewed/checked CI with editor/runner/prompt compiler; verify assigned full SHA. Integrate CB after binding and real matched-profile review. Research/document base D0 is 1bfcc50e204797862b2bbc014fce00e4694c122c; it is not an automatic launch base.
- **Interfaces:** ReferenceBinding/ResolveReferenceBindings and physical reference_manifest, KVD-WORKER/2.0.0; stable subject/media IDs, per-window Picture/Subject labels derived from actual sockets.
- **Acceptance:** User can bind supplied identity/appearance images to specific subjects in two scenes; reordering/clearing/relinking and presence validate; quotas enforced, no unresolved labels; Canny motion remains separate. Real no-ref/ref/cleared comparisons on compatible Ref2VA+Fun profile, identity across a deliberate cut and resource/quality limits reviewed. No perfect fidelity promise.
- **Checks:** Future python -m pytest tests/references; real browser bindings/save/reload; native graph manifest/socket inspection; actual two-scene GPU comparison and hashes/memory receipt. Metadata-only references cannot satisfy this.
- **Environment:** Explicit supplied/licensed images and approved existing runtime/models; missing assets/backend block the identity variant, while manual/no-ref remains usable. No automatic image creation/search/uploads/downloads.
- **GPU ownership:** One allocated sequential H3/shared-ComfyUI owner for combined image+control test; no concurrent load/inference/settings changes.
- **Publication/review:** NOT STARTED; this M0 does not authorize implementation/publishing. Later assignment supplies scope; one owner includes ordinary tests/docs, separate AO reviewer, fixes return to owner. No private assets/session/auth/machine diagnostics in public outputs.
- **Status/blockers:** PROPOSED / NOT STARTED; required common SHA, owner, implementation/environment/publication allocation not supplied. GPU NOT PERFORMED. Technical gates above are future blockers, not evidence of a failed run.

## Journal

First M0 established the short proof and shared-base policy. M0-V2V-REVISION adds this outcome for the updated product direction and proposed 2.0.0 interfaces. No code, fixture/media generation, dependency install, inference or task launch occurred.
