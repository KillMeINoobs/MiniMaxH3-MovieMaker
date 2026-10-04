# Collaboration rules

- Read [the brief](docs/PROJECT_BRIEF.md), [research](docs/RESEARCH.md), [contracts](docs/CONTRACTS.md) and the assigned card in [the journal](docs/tasks/INDEX.md) before changing this project. The journal is Markdown, not an AO task scheduler.
- Keep assignments within their milestone. Current scope is M0 proposed design; no extension exists. M1/M2 require a subsequent human decision and assignment. This does not prohibit later authorized implementation.
- Preserve the brief byte for byte; record decisions separately. M0 names, formats and interfaces are proposals until implemented and verified.
- Work only in the assigned AO worktree and feature branch; verify the assigned base SHA. Do not change shared Git config, remotes, authorization, another worktree or the primary checkout.
- Distinguish source facts, inferences, proposals, unknowns, CPU/media checks and real GPU results. Record revisions, paths, model identities and licenses. Mocks and publisher examples are not our GPU receipts.
- Use integer 24 FPS intervals `[start,end)`. Useful coverage is exact; inference limits include padding/context. Source RGB, structural control, appearance references and inpainting have distinct roles.
- One first owner controls shared schemas, package metadata, lockfiles and skeleton. Downstream starts from a recorded, integrated, checked common commit, never another worker's unmerged branch. Interface changes go through that owner.
- Starting policy: at most two implementing workers simultaneously. One worker owns each outcome, its ordinary tests and docs. Future code review uses a separate AO reviewer; fixes return to the owner. Workers do not launch workers or nested orchestrators.
- GPU, ComfyUI installation, ports, output, venv and model settings are shared resources. Authorized GPU/ComfyUI work is sequential with one named resource owner. Cloud workers must not assume the user's hardware is available.
- No paid services, asset uploads, weight downloads, installs or changes to working ComfyUI without authorization covering the action. Do not scan personal files for inputs. Missing resources are blockers.
- Optional Depth/Pose backends must remain optional at import. Preserve native queue/execution/progress/interruption/model management; avoid recursive HTTP self-queueing and silent source passthrough for unfinished results.
- Verify the assigned outcome and report meaningful checkpoints, blockers and artifacts through `ao report`. Publishing follows task scope. M0 authorizes docs commit, push and one draft PR to main; automatic merge is not requested.
