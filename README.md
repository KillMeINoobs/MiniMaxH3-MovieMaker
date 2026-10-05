# ComfyUI-KMIN-VideoDirector

A proposed complete local ComfyUI node collection for video creation/transformation, timeline editing and supplied usable workflows. **V2V is the main first mode:** gameplay or low-poly Blender video → photorealistic cinematic output, with structural control, editable per-scene prompts, optional subject appearance images and measured continuity across windows/scenes. Photorealism is a goal to evaluate, not a demonstrated result. Higgsfield and DaSiWa are workflow/visual inspiration, not equivalent backends.

**Second M0 documentation revision only. No extension, installation package, implemented schemas, executable nodes, ready workflow or GPU result exists here. GPU NOT PERFORMED.** Windows RTX 5070 Ti 16 GB / 32 GB RAM is the target; fit is UNVERIFIED. WSL is not required. First M0 base is `1bfcc50e204797862b2bbc014fce00e4694c122c`, published separately from main; this revision does not merge into main.

The first planned proof is: short clip → real 24 FPS normalization → legal windows → Canny preview → native H3 ControlNet → trim padding → assemble/export, with a comparable control-off run. It must work without character references; source RGB must not become a hidden appearance reference. VID2VA is our workflow name, not a separate checkpoint.

Read these in order:

1. [Original brief](docs/PROJECT_BRIEF.md), preserved byte for byte.
2. [Latest V2V product direction](docs/PRODUCT_DIRECTION_V2V.md), explicit supersessions and requirements reconciliation.
3. [Research](docs/RESEARCH.md), actual native/ControlNet/enhancer/Motion-Context/Qwen/UI source, revisions/licenses and unknowns.
4. [Architecture](docs/ARCHITECTURE.md) and [contracts 2.0.0](docs/CONTRACTS.md), proposed bounded execution and shared records.
5. [Proposed node catalog](docs/NODE_CATALOG.md) and [future workflow specification](docs/WORKFLOW_SPEC.md), inventory/wiring and acceptance, not executable assets.
6. [Staged plan](docs/PLAN.md) and [task journal](docs/tasks/INDEX.md), short proof → editor/runner → scene prompts → optional identity → continuation → ready V2V workflows; then additional controls/creation modes.
7. [Collaboration rules](AGENTS.md).

Pinned native code aligns frames upward to `17*k+5` at 24 FPS. Under the strict 15-second project limit, the largest legal inference window is 345 frames; a 360-frame useful clip needs multiple windows. See [the constraint table](docs/RESEARCH.md#constraints) for shape limits, training guidance and product policy.

Arbitrary input duration is handled step by step with disk-backed preprocessing, bounded analysis/render windows, quotas and resumable receipts. Scene/shot markers remain distinct from inference-window edges. A Qwen VLM analyzer and optional text enhancer draft editable H3 prompts; H3's embedded Qwen encoder is separate. Optional images explicitly bind subjects across scenes; continuation state resets at deliberate cuts. These are product requirements with explicit later gates, not implemented features.

Neither `test-1.mp4` nor `video_minimax_h3_fun_controlnet_union_test.json` was supplied. No user asset, model weight or third-party implementation was copied into this repository. No repositories were cloned or dependencies installed. Original brief blob `77e34e02374483fc19be006dc5d5b78e40f15042` retains SHA256 `81B86AB34ADD27455F5A6B4F37652050A5DDE0FEEB024F25616FF1D53D6C513B`; its working bytes are also preserved despite checkout line-ending differences.

The project license is **not selected**. Core/extensions and model licenses differ; future borrowing/usage needs the [recorded checks](docs/RESEARCH.md#licenses). The local MVP has no model redistribution or paid inference dependency.

M0 ends with documentation checks, commit and this revision's own-branch push/compare handoff. A previously recorded PR/auth blocker is not retried here. All implementation/backlog tasks remain NOT STARTED and need later assignments; no runtime/GPU work is authorized by these documents.
