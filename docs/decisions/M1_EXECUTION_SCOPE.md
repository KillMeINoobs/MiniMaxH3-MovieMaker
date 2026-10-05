# M1 foundation execution scope

Accepted documentation base C0: `7960568eff779c8c35c3d28a985a243368b91c26`.
The merged base includes M0 final head `9dac703183e3e56929432054f5ebc6d63c26d8e2`.
The original brief remains unchanged. This decision records the subsequent
implementation assignment; earlier M0-only authorization statements describe
that completed documentation stage.

The human authorized M1 implementation, CPU synthetic checks, English-first
nodes with a persisted Russian switch, and shared-runtime registration/load/UI
checks. Workers must never enqueue a workflow, load a generation model, invoke
H3/VLM/enhancer inference, download weights, or inspect generated user-video
output. M1-04 is a workflow handoff for the human to run. GPU NOT PERFORMED until
the human supplies evidence. M2/M3 remain gated.

## Implementation plan

1. Write contract conformance and rejection tests, then implement bundled
   JSON Schemas and immutable stdlib records. Validate structure and semantic
   invariants separately. Keep optional features serializable while explicitly
   rejecting unsupported runtime requests.
2. Implement canonical UTF-8 serialization, project-relative resolution,
   atomic save/load, settings inheritance, identifiers and cache conventions.
   Add an explicit, narrow v1-example migration that writes a new file and
   preserves the input; other v1 data requires a new migration profile.
3. Publish callable `KVD-WORKER/2.0.0` protocols and typed operation envelopes.
   Discover independently owned node modules without edits to shared package
   files. Do not register fake media or generation implementations.
4. Implement Project JSON/load/save/validation nodes with stable class IDs,
   keys and port types. Add a persisted, discoverable KVD EN/RU setting and
   scoped presentation hooks, cohesive colors and concise bilingual help.
5. Verify synthetic CPU contracts, schema conformance, absent optional imports,
   serialization, migration, registry and presentation. Check real ComfyUI
   registration/frontend/workflow reload only after confirming its exact
   installation, idle queue and confined deployment/restart route.
6. Record evidence and limitations; inspect the public diff for private paths,
   assets and credentials. Commit and push the assigned feature branch,
   prepare one draft PR and report the exact checked candidate CF for separate
   review. A worker does not self-label the outcome reviewed or merge it.

## Ownership and limits

Foundation owns schemas/contracts/errors/version, root package/dependencies,
extension discovery, frontend presentation/settings/translations, README and
central journal. Downstream owners add their own node modules/tests/docs using
the checked interfaces. Shared amendments return to foundation.

Runtime dependencies are kept to the Python standard library. JSON Schema
conformance can additionally be checked with an existing independent validator
in the verification environment. No shared venv changes are permitted.

DaSiWa is visual inspiration only; no code or assets are copied. The existing
source ledger stays pinned. Project license selection is recorded separately;
model licenses do not become this package's license.

## Implementation and review checkpoint

M1 now implements the shared records, Project nodes and presentation foundation
in the [actual handoff](../FOUNDATION_HANDOFF.md). The
[validation receipt](../validation/M1_FOUNDATION.md) records synthetic CPU,
Windows filesystem and interface checks separately from blocked live UI work.
An independent review requested concrete F1-F9 corrections; the owner supplies
regressions and a new full pushed candidate for incremental review. No CF or
downstream acceptance follows from a draft PR or owner checks.

The existing Desktop restart cannot be operated safely by available native
automation. The supported instance-picker UI restart is reserved for the human
after the corrected snapshot is reviewed and deployed. No alternate private
IPC/lifecycle endpoint, shell kill, second server or stale CLI restart is used.
Foundation retains shared-runtime ownership and generation reservation is NONE.
