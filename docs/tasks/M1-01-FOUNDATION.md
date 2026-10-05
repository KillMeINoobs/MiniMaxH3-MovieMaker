# M1-01 — Portable project and shared foundation

- **Goal:** Load/save and validate portable Projects; downstream owners share one checked interface.
- **Owner/status:** Assigned foundation owner; IMPLEMENTED DRAFT, incremental independent review pending. CF unaccepted; actual registration/browser gates BLOCKED.
- **Base:** Accepted C0 `7960568eff779c8c35c3d28a985a243368b91c26`, including M0 final `9dac703183e3e56929432054f5ebc6d63c26d8e2`. The preserved brief and source ledger are unchanged.
- **Scope:** Validated/versioned 2.0.0 records, schemas, canonical JSON, settings inheritance, ordinary local Project I/O with relative-path checks and cooperative publication/revision leases, explicit migration/errors/cache conventions, import-safe extension discovery and four Project nodes. Persisted English/Russian presentation with stable semantics. The [local storage decision](../decisions/M1_LOCAL_STORAGE_SCOPE.md) supersedes earlier OS isolation claims.
- **Shared ownership:** schemas/, kmin_video_director/contracts/, common errors/version/registration/helpers, root package/dependencies/lockfile, frontend settings/translations/tokens, notices, README and central PLAN/INDEX. Owned downstream modules/tests extend through documented discovery without changing shared files.
- **Non-goals:** Media decoding, H3/VLM/enhancer inference, model downloads, timeline editor, fake downstream operations or worker GPU generation.
- **Read paths:** AGENTS, README, preserved brief, PRODUCT_DIRECTION_V2V, RESEARCH, ARCHITECTURE, CONTRACTS, NODE_CATALOG, WORKFLOW_SPEC, PLAN, INDEX and all M1 cards. Later human direction is recorded separately in [execution scope](../decisions/M1_EXECUTION_SCOPE.md).
- **Implemented outputs:** 16 schemas; 15 conformance record fixtures; contracts/common registration/root package; web/; contracts/import/UI tests; [handoff](../FOUNDATION_HANDOFF.md); [validation](../validation/M1_FOUNDATION.md); NOTICES; synthetic Project UI workflow.
- **Interfaces:** `KVD-WORKER/2.0.0`, `kmin.*` schema2.0.0. Actual import paths/types/call signatures and all-nine typed examples are in the handoff. No registered handler for ProbeMedia, NormalizeMedia, PlanWindows, PrepareWindow, BuildControl, CompileWindowPrompt, ExpandNativeRender, FinalizeWindow or AssembleExport.
- **CPU acceptance:** Windows synthetic records/import/serialization/schema/I/O/conformance and meaningful review regressions pass. Relative Unicode paths, safe integers/u64 seeds, version/features, malformed fields and source-preserving migration are covered. Optional dependencies are absent from imports.
- **UI acceptance:** Helper semantics pass; discoverable persisted EN/RU switch and scoped presentation are implemented. Actual frontend import/console/layout/screenshots/language save-reload remain BLOCKED pending the supported human Desktop restart. No live PASS claimed.
- **Environment:** Isolated verification venv only; Python stdlib runtime, no required WSL. Windows normal-use I/O verified; POSIX runtime/FIFO checks NOT PERFORMED. Prior adversarial checks are historical, not current storage acceptance.
- **Resource ownership:** Sole shared-ComfyUI registration/UI owner until explicit release. Own namespaced snapshot only; no core/other-pack/settings changes or lifecycle workaround. Generation reservation NONE; GPU NOT PERFORMED.
- **Publication/review:** Own feature branch/SSH push and one draft [PR2](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2) are authorized. Exact corrected SHA/clean tree/receipts go through AO for separate review. No main merge or self-review claim.
- **Dependent gate:** No media/adapter starts until coordinator accepts the exact reviewed/checked CF with actual API and live receipts. No integration of later SHAs without assignment.

## Journal

M0 was documentation only. Later human direction authorized M1 implementation
and registration/UI-only runtime checking. Initial lock was released after C0,
brief and private native/client preflight checks. The first published candidate
was `12feb672faafadd417936a92b0a13f9bd4d336e3`; follow-up
`260a37dadc04477d1d0779f188ffaf5ebff0c35b` fixed EOF, per-side overhead and
control/stream checks. Separate review requested F1-F9 corrections; owner
regressions reproduced them and the next corrected candidate is pinned through
AO/PR. See the validation matrix for each fix. Artifact publication is not CF
acceptance. Live checks stay BLOCKED; shared-runtime ownership stays retained.

The final review of `fdce306ce6b7ac4c38491b593b6a821555d224c3` confirmed F2-F9
resolved, found F1b still open for in-place junction changes, F10 raw cyclic-path
errors and source-derived F11 FIFO blocking. Later human direction explicitly
narrowed storage to stable local folders and regular files. The owner preserved
F10 typed resolution, replaced the special isolation layer with standard Python
I/O and retained revision/lease semantics. Historical F1b is not labelled fixed;
two obsolete adversarial rename tests are retired. Normal-use/error regressions
and the new exact candidate require review against the declared revised contract.
Schema/interface 2.0.0, nodes and nine signatures remain unchanged. See validation
for fresh counts; no approval is inherited from the earlier head.
