# M2-03 — Editable scene intelligence and H3 prompt recipes

- **Goal:** A user reviews proposed cuts and gets evidence-linked editable scene prompt drafts from a real supported vision backend.
- **Scope:** Streamed detector proposals/manual overlay; bounded Qwen vision sampling/coverage/uncertainty; editable observations and accepted recipe; optional text-enhancer guide/manifest adapter, manual/model-free fallback; exact per-window compilation and scoped model teardown. One scene-intelligence outcome plus ordinary tests/docs.
- **Non-goals:** Automatic unreviewed scene edits, inferred dialogue/identity, source-video appearance routing, H3 encoder as VLM, video-consuming instruct GGUF assumption, hosted Context-IR equivalence or paid dependency.
- **Inputs/read paths:** AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/PRODUCT_DIRECTION_V2V.md, docs/RESEARCH.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/NODE_CATALOG.md, docs/WORKFLOW_SPEC.md, docs/PLAN.md, docs/tasks/INDEX.md and this card.
- **Outputs/new paths (proposed):** kmin_video_director/analysis/, prompts/, adapters/prompt_enhancer/, web/prompts/; tests/analysis/, tests/prompts/; docs/validation/M2_PROMPTS.md. Shared optional dependency metadata changes through foundation.
- **Dependencies/base commit:** Actual checked CT with working editor/runner/M1 receipts. Verify full assigned SHA/interfaces; review/check/integrate CI before identity/state workers start. Research/document base D0 is 1bfcc50e204797862b2bbc014fce00e4694c122c; it is not an automatic launch base.
- **Interfaces:** DetectShots/AnalyzeScene/DraftPrompt/CompileWindowPrompt, DetectionProposal/SceneAnalysis/PromptRecipe; KVD-WORKER/2.0.0; independent h3.base/1 and h3.ref/1 guide/provider pins.
- **Acceptance:** Real supported Qwen3-VL-4B Transformers or declared tested alternative; every scene chunk <=12 s/<=16 samples with times/hashes/gaps, bounded pixels/tokens and resampling; detector false cuts/fades/HUD correction; observed vs desired style; three/six-block order, dialogue locks and exact window timing; accepted text not overwritten; optional backend absence keeps manual path; renderer rejects enhancer size/duration mismatches. Actual process release/H3 load peak measured; unavailable VLM is BLOCKED, not PASS.
- **Checks:** Future python -m pytest tests/analysis tests/prompts; detector/media integration, compiler/manifest fixtures, real VLM/draft/edit/save and optional enhancer/manual runs, targeted cancel/process-exit/memory receipts. Syntax validation is not semantic/GPU quality.
- **Environment:** Pre-existing or separately authorized VLM/runtime/service; exact Transformers/processor/model/quantization or multimodal endpoint pin; no mandatory WSL/server/backend; no source upload or credentials in project state.
- **GPU ownership:** One allocated sequential resource owner for VLM/enhancer/H3 testing. Owned process teardown completion precedes H3; unrelated API-server residency must be explicitly handled, never globally killed.
- **Publication/review:** NOT STARTED; this M0 does not authorize implementation/publishing. Later assignment supplies scope; one owner includes ordinary tests/docs, separate AO reviewer, fixes return to owner. No private assets/session/auth/machine diagnostics in public outputs.
- **Status/blockers:** PROPOSED / NOT STARTED; required common SHA, owner, implementation/environment/publication allocation not supplied. GPU NOT PERFORMED. Technical gates above are future blockers, not evidence of a failed run.

## Journal

First M0 established the short proof and shared-base policy. M0-V2V-REVISION adds this outcome for the updated product direction and proposed 2.0.0 interfaces. No code, fixture/media generation, dependency install, inference or task launch occurred.
