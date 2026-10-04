# Durable task journal

This directory is the project's Markdown journal, **not an AO built-in task/dependency system**. Cards describe proposed outcomes; no worker is launched by them. All interface/file names are proposals. [Plan](../PLAN.md), [contracts](../CONTRACTS.md), [research](../RESEARCH.md), [architecture](../ARCHITECTURE.md) and [brief](../PROJECT_BRIEF.md) form the handoff.

## Status and ownership

| ID / card | Proposed owner | Status | Blocker / integration rule |
|---|---|---|---|
| M0-DOCS | Current documentation worker | Document checks passed; ready for human review | Draft PR handoff; no implementation/GPU work |
| [M1-01 foundation](M1-01-FOUNDATION.md) | One foundation owner, unassigned | PROPOSED / NOT STARTED | Human M0 decision + exact C0 |
| [M1-02 media](M1-02-MEDIA.md) | Media owner, unassigned | PROPOSED / NOT STARTED | Integrated checked CF |
| [M1-03 H3](M1-03-H3.md) | Adapter owner, unassigned | PROPOSED / NOT STARTED | CF for start; CM integrated before final adapter integration |
| [M1-04 GPU gate](M1-04-GPU-GATE.md) | Single named resource owner, unassigned | GPU NOT PERFORMED / NOT STARTED | CH + explicit environment/assets/model authorization and availability |
| [M2-01 editor](M2-01-EDITOR.md) | Editor owner, unassigned | PROPOSED / GATED | Real M1 receipt accepted at CG |
| [M2-02 runner](M2-02-RUNNER.md) | Runner owner, unassigned | PROPOSED / GATED | CG; editor integrated before final joint UI checks |

Starting policy: <=2 implementing workers concurrently. Shared schemas/package/lockfiles/skeleton have exactly one first owner. GPU/ComfyUI/ports/output/venv/models have one sequential resource owner, named by AO session ID before access; there is **no current reservation**. Future code review uses a separate AO reviewer and fixes return to owner. No built-in subagents or nested orchestrators are implied.

## Common commit register

| Label | Meaning | Full SHA / current status |
|---|---|---|
| B0 | Verified original main/base | `8e8cf7253862f94b7787d7065babf2878064ef82` |
| C0 | Accepted, integrated M0 docs | UNASSIGNED; coordinator records after human review/integration |
| CF | M1-01 integrated/reviewed/checked foundation | NOT CREATED |
| CM | CF + integrated/checked M1-02 media | NOT CREATED |
| CH | CM + integrated/reviewed M1-03 adapter | NOT CREATED |
| CG | CH + reviewed real M1-04 evidence and accepted gate | NOT CREATED; GPU NOT PERFORMED |
| CE / CR | Editor / runner outcome integration commits | NOT CREATED |
| CM2 | Both M2 outcomes integrated, checked and reviewed | NOT CREATED |

Each launch record must include task/owner AO session, actual workspace/branch/HEAD, exact full base SHA, dependencies present on that SHA, interface version, changed-area ownership, resources, publication authorization, acceptance receipts and reviewer. A symbolic label alone is insufficient to start. Integration means reachable on the shared reviewed branch, with its checks run; never assume another branch's files or use an unmerged PR as if in base.

Dependency order: `C0 → M1-01 → CF → (M1-02, M1-03) → CM → M1-03 integration → CH → M1-04 → CG → (M2-01, M2-02) → CM2`. Media and adapter can start from CF; final adapter integration includes CM. Editor and runner can start from CG on agreed interfaces/areas; final joint verification includes both integrated outcomes. Record every actual common SHA before the next phase.

## Journal update policy

Append meaningful decisions/checkpoints/blockers/receipts to the relevant card, update this index and record integration SHAs. No task advances by elapsed time or an optimistic checkbox. Ordinary unit/media tests and docs remain with the outcome owner; GPU evidence is labeled separately. Artifacts reported through AO do not imply task completion. Public receipts redact local machine/session diagnostics and asset paths; no personal media is published without explicit authorization.

M0 final commit/PR are supplied through AO handoff to avoid a self-referential commit hash. Publishing only M0 docs is authorized here. Later tasks await their own assignment/authorization; no merge is automatic.
