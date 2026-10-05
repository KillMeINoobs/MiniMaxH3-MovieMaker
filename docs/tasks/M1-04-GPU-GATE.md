# M1-04 — Human generation handoff and GPU decision

The later human direction supersedes the M0 worker-GPU execution plan. Workers
prepare a real loadable workflow and manual instructions. **Only the human runs
it and supplies generation evidence. GPU NOT PERFORMED until then.**

- **Goal:** The human can load the real M1 V2V workflow, run it deliberately and provide evidence for a controlled/off comparison and resource/quality decision.
- **Scope:** Registration/schema/preflight/serialization checks; actual workflow and relink/setup/manual instructions after media/adapter integration. Explicit settings/profile/seed/control and source-audio policy, exact useful-frame trimming/assembly contracts and visible expected receipts. Route code failures to outcome owners.
- **Non-goals:** Worker prompt submission/node execution/model load/H3/VLM/enhancer inference, paid calls, weights/downloads, generated user-video inspection, asset search/copy/upload, automatic M2/M3 launch or CPU/mock GPU-fit claims.
- **Read paths:** AGENTS, README, preserved brief, PRODUCT_DIRECTION_V2V, RESEARCH, ARCHITECTURE, CONTRACTS, NODE_CATALOG, WORKFLOW_SPEC, PLAN, INDEX and M1 cards; [current scope](../decisions/M1_EXECUTION_SCOPE.md) wins over old execution wording.
- **Outputs:** Real UI/API workflow assets containing actual registered nodes, setup/relink instructions, exact profiles/component identities and a human evidence checklist. Future docs/validation/M1_GPU.md stays GPU NOT PERFORMED until actual supplied evidence. Personal media/output stays private.
- **Dependencies:** Exact reviewed/checked CH containing CF+CM+adapter. Foundation's synthetic Project fixture does not satisfy this workflow outcome. Separate code review precedes the handoff; fixes return to owners and yield a new checked CH.
- **Interfaces:** KVD-WORKER/2.0.0 and pinned installed node/core/frontend/model/quantization/kernel identities. No guessed or silently switched profile.
- **Human acceptance evidence:** Same-setting controlled/off samples, no hidden refs/inpaint, exact useful frames/24FPS/geometry/pad/audio, declared timings/peak resources and honest quality/control judgment. Two-window F=360, lifetime and cancellation are human/manual evidence items, not authorized worker runs.
- **Checks:** Worker read-only registration/load/serialization/preflight only. No enqueue or validator that instantiates generation models. CPU/media/static/browser evidence stays separate from human GPU evidence.
- **Resource ownership:** No worker GPU generation reservation. Registration/UI runtime access is sequential under the explicitly allocated owner. Do not modify another installation or launch a second server.
- **Publication/review:** Future assignment identifies exact base/owner/scope; coordinator accepts the evidence gate. No main merge, private diagnostics or media in public outputs.
- **Status:** GATED on CH. GPU NOT PERFORMED. M2/M3 do not open automatically.

## Journal

M0 proposed a short real proof. The later human scope now assigns generation to
the human and implementation/preflight/workflow preparation to workers. Keep
this boundary in every workflow instruction and result receipt. Missing human
evidence is an unperformed gate, not a failed run or a CPU/mock PASS.
