# M1-02 — Source to real CFR24, legal plan and accurate export

- **Goal:** Adding a source gives measured 24 FPS media, understandable legal windows and an exact CPU export.
- **Scope:** Actual-PTS probe/resampling to disk; canonical/hash manifest; balanced no-context windows; bounded geometry/pad preparation; global PCM/sample mapping; checked assembly and scoped caches. Own ordinary logic/media tests/docs.
- **Non-goals:** Neural inference, model loading, timeline editor, source appearance refs, continuation or queue recovery.
- **Inputs/read paths:** AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/PRODUCT_DIRECTION_V2V.md, docs/RESEARCH.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/NODE_CATALOG.md, docs/WORKFLOW_SPEC.md, docs/PLAN.md, docs/tasks/INDEX.md and this card.
- **Outputs/new paths (proposed):** kmin_video_director/media/, planning/, assembly/, nodes/media/; tests/media/, tests/planning/, tests/assembly/; docs/validation/M1_MEDIA.md. Shared schemas/registration/dependencies stay foundation-owned.
- **Dependencies/base commit:** Start only on reviewed/integrated/checked CF with full assigned SHA and actual 2.0.0 interfaces. Integrate/check CM and record its SHA; adapter's final integration consumes CM, not an unmerged branch. Research/document base D0 is 1bfcc50e204797862b2bbc014fce00e4694c122c; it is not an automatic launch base.
- **Interfaces:** ProbeMedia, NormalizeMedia, PlanWindows, PrepareWindow, AssembleExport; KVD-WORKER/2.0.0. Initial context none; future context-aware planner extensions negotiate through foundation.
- **Acceptance:** Actual decoded F and PTS 1/24; L=1/346/360/1000 coverage, legal N/pad trimming; fractional/VFR/gaps/EOF; source-duration rounding/clamp provenance including D=1/120 s → R=0/F=1/error=1/30 s. Ordinary D>=1/48 s normalization error <=1/48 s; minimum-one-frame 0<D<1/48 s error <1/24 s. +/- audio offset and boundary impulses/global Q/one encode/codec delay; mute/no audio; display rotation/SAR/4:3/portrait/off-grid/odd-codec behavior; Unicode/spaces; streamed working set/disk quota. Export duration error <=1 frame without accumulation, PCM rounding <=1 sample.
- **Checks:** Future python -m pytest tests/media tests/planning tests/assembly; approved synthetic frame-number/impulse media with recorded ffprobe decoded PTS/counts/sample/dimension receipts and peak process RAM; git diff --check. CPU export is not H3 evidence.
- **Environment:** Existing approved FFmpeg/ffprobe or reviewed equivalent; record exact binary/build/license/version. No personal-media search, downloads or ComfyUI changes; named chat assets are not supplied.
- **GPU ownership:** None. Media/adapter may implement on CF within initial <=2 policy; all real shared-runtime validation waits for allocated sequential owner.
- **Publication/review:** NOT STARTED; this M0 does not authorize implementation/publishing. Later assignment supplies scope; one owner includes ordinary tests/docs, separate AO reviewer, fixes return to owner. No private assets/session/auth/machine diagnostics in public outputs.
- **Status/blockers:** PROPOSED / NOT STARTED; required common SHA, owner, implementation/environment/publication allocation not supplied. GPU NOT PERFORMED. Technical gates above are future blockers, not evidence of a failed run.

## Journal

First M0 established the short proof and shared-base policy. M0-V2V-REVISION reconciles this outcome with the updated product direction and proposed 2.0.0 interfaces. No code, fixture/media generation, dependency install, inference or task launch occurred.

Document-review correction: distinguish the ordinary half-frame rounding bound from the minimum-one-frame duration clamp; retain exact F CFR frames and the existing export acceptance. The PLAN receipt records five exact rational boundary checks; actual media tests remain future work.
