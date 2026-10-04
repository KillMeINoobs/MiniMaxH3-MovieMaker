# ComfyUI-KMIN-VideoDirector

A proposed local ComfyUI custom-node package for restructuring gameplay/CGI video with MiniMax H3 structural control and a small timeline interface.

**M0 documentation only. No extension, installation package, implemented schemas, executable nodes or GPU result exists here. GPU validation NOT PERFORMED.** Windows RTX 5070 Ti 16 GB / 32 GB RAM is the user's target, not verified worker capability or a fit guarantee. WSL is not required.

The first planned proof is: short clip → real 24 FPS normalization → legal windows → Canny preview → native H3 ControlNet → trim padding → assemble/export, with a comparable control-off run. It must work without character references; source RGB must not become a hidden appearance reference. VID2VA is our workflow name, not a separate checkpoint.

Read these in order:

1. [Authoritative user brief](docs/PROJECT_BRIEF.md), preserved unchanged.
2. [Research and compatibility evidence](docs/RESEARCH.md), pinned primary sources and unknowns.
3. [Architecture proposal](docs/ARCHITECTURE.md), execution/media responsibilities.
4. [Format/interface proposals, version 1.0.0](docs/CONTRACTS.md), common worker contract.
5. [M1/M2 plan and acceptance](docs/PLAN.md), GPU gate before the larger editor.
6. [Durable task journal](docs/tasks/INDEX.md), ownership/integration order.
7. [Collaboration rules](AGENTS.md).

Pinned native code aligns frames upward to `17*k+5` at 24 FPS. Under the strict 15-second project limit, the largest legal inference window is 345 frames; a 360-frame useful clip needs multiple windows. See [the constraint table](docs/RESEARCH.md#constraints) for shape limits, training guidance and product policy.

Neither `test-1.mp4` nor `video_minimax_h3_fun_controlnet_union_test.json` was supplied to M0. No user asset, model weight or external source code was copied here. No repositories were cloned or dependencies installed. The explicitly supplied brief retains SHA256 `81B86AB34ADD27455F5A6B4F37652050A5DDE0FEEB024F25616FF1D53D6C513B`.

The project license is **not selected**. Core/extensions and model licenses differ; future borrowing/usage needs the [recorded checks](docs/RESEARCH.md#licenses). The local MVP has no model redistribution or paid inference dependency.

M0 ends with documentation review. M1/M2 are proposed work, not started or authorized by this repository's existence.
