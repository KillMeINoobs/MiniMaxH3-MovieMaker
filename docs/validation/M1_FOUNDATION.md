# M1 foundation validation

Accepted base C0: `7960568eff779c8c35c3d28a985a243368b91c26`, containing M0
final head `9dac703183e3e56929432054f5ebc6d63c26d8e2`. This receipt covers the
M1-01 implementation and review follow-up. Exact pushed candidate and clean-tree
receipts are recorded in AO and [draft PR #2](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2).
It does **not** accept CF; a separate reviewer checks the pinned final candidate.

## Evidence levels

| Check | Result / scope |
|---|---|
| Synthetic Python contracts/import/I/O/conformance | PASS: 103 tests on Windows; one POSIX FIFO test skipped, no failures. |
| Draft 2020-12 schemas and examples | PASS: 16 exported schemas; 15 synthetic record fixtures; schema bytes match declarative source. |
| Project serialization/migration | PASS: Unicode/spaces, immutable settings, full u64 seeds, duplicate keys, version/features, explicit migration/source preservation. |
| Ordinary local I/O failures | PASS: read/staging/flush/publication failures preserve old bytes and clean temporary files. A post-publication cleanup error logs a redacted warning and returns the committed save. |
| Concurrent Project API writers | PASS: newer revision remains saved; publish-time lease defers a competing writer with retryable PROJECT_BUSY. |
| Invalid/cyclic path resolution | PASS: save/load/migration/locator/explicit asset checks return redacted PROJECT_IO_ERROR for a cyclic selected root; cyclic migration source/destination paths preserve original bytes. |
| Optional dependencies absent | PASS: subprocess blocks media/model/ComfyUI/schema packages; four Project classes still import and expose inputs. |
| Nine downstream callable interfaces | PASS: typed examples bind actual signatures; every unimplemented operation rejects registry dispatch; no handler invoked. |
| EN/RU helper and checker regressions | PASS: 11 Node checks; pure presentation invariants plus ten actual-module tests against a synthetic host. They do not prove browser appearance/persistence. |
| Frontend syntax | PASS: shared presentation, extension and opt-in checker parse. |
| Diff/brief/ledger/privacy | Checked before publication; final exact receipts are recorded with the candidate in AO. |
| Live `/object_info` registration | PASS at reviewed `20541f938306ff6bbf80c01565fd318ea3bcbd82` after the human restart: four actual classes, own module, matching inputs/outputs; readonly MCP fixture validation has zero errors and one intentional disconnected-load warning. |
| Actual frontend import/console/layout | BLOCKED: own fixture load aborted with a null-canvas error; the old checker incorrectly logged PASS. No accepted EN/RU screenshots or updated live behavior claimed. Foreign-pack errors are recorded separately. |
| Language persistence + native workflow save/reload | BLOCKED in actual browser; pure helper checks are not a browser receipt. |
| POSIX local I/O/FIFO runtime | NOT PERFORMED in this Windows session; platform-specific FIFO test is skipped. Windows unit test uses a synthetic nonregular stat result to check rejection before open. |
| CPU media decoding / real user video | NOT PERFORMED by foundation. |
| H3/VLM/enhancer generation / GPU / quality / fit | NOT PERFORMED. No queue submission, model load, weight download or output inspection. |
| CI | No checks registered on the draft PR; no CI PASS. |

Commands used in the isolated verification environment:

```text
.venv/Scripts/python -m pytest tests/contracts tests/imports -q
node --experimental-vm-modules --test tests/ui/presentation.test.mjs tests/ui/verification.test.mjs
node --check web/common/presentation.js
node --check web/kvd.js
node --check web/zz_verification.js
git diff --check
git diff --cached --check
git diff 7960568eff779c8c35c3d28a985a243368b91c26 HEAD --check
```

Synthetic manifests labelled `mock`/`source_only`/`missing` are conformance data,
not actual video artifacts. Direct Project-only node tests run in temporary
folders. No native execution or generated pixels are produced by these tests.

## Human restart and own checker follow-up

Independent [source/CPU review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5411533237)
approved exact `20541f938306ff6bbf80c01565fd318ea3bcbd82` under the revised local
storage assumptions. Its 97 committed deployment files byte-matched that tree.
The human restarted the existing Desktop instance; new process/start evidence,
unchanged deployed hashes, one live listener and an idle queue were reconciled
privately. Live ComfyUI 0.38.2 / Python 3.13.12 / frontend 1.53.6 registered all
four Project classes from this pack. MCP search/get and the live catalog agree.
No workflow or node was executed.

The dedicated opt-in browser fixture showed an aborted workflow load and
`getCanvas: canvas is null`, followed by an invalid checker PASS. The old checker
started loading inside setup and ignored the native result; installed primary
sources show load failures can resolve to `false`. The false-PASS defect is reproduced by
synthetic tests using the actual checker module. Startup timing remains a
source-backed hypothesis; the correction has not yet been verified in the live
browser. Unrelated Impact-module/rgthree errors and legacy warnings stay outside
this owner fix; global silence across foreign packs is not acceptance.

The correction waits for the declared `afterLoadGraph` hook, checks graph/canvas
readiness and requires each native load's successful boolean result. It checks
the first loaded fixture against original semantic data, including widget values
and links, and exercises a custom title through language changes and reload;
failed roundtrips restore the original KVD language when possible. The display
banner names the checked language without implying an EN/RU roundtrip.
An aborted roundtrip does not publish a new saved graph for the persist phase.
Native metadata loads skip asset scans. The timer only dispatches after the
hook returns; it does not infer readiness from a delay. APIs were verified in
the installed primary source and public
[v1.53.6 application](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/scripts/app.ts)
and [extension types](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/types/comfy.ts).

[verification.test.mjs](../../tests/ui/verification.test.mjs) covers ordinary-page
inertness, one deferred start after native loading, rejected/unknown load
results, corrupted first-load data, failed roundtrip/preference restoration,
unavailable canvas, premature readiness, custom-title corruption, and successful synthetic roundtrip and
persist phases. Node uses its experimental VM-module flag only for this
isolated host simulation. It is not a ComfyUI browser runtime test. The corrected
candidate requires separate pinned review before the deployed files change.
Screenshots were not obtained because the AO capture timed out; actual console,
errors, catalog and restart receipts remain private AO artifacts. CF remains
unaccepted and shared-runtime ownership is retained.

## Historical review and current owner verification

Reviews requested changes on `260a37dadc04477d1d0779f188ffaf5ebff0c35b` and
`fdce306ce6b7ac4c38491b593b6a821555d224c3`. The final
[exact fdce receipt](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5409824233)
confirmed F2-F9 resolved, F1b still open, F10 raw path errors and source-derived
F11 FIFO blocking. The human then explicitly narrowed storage in the
[local storage decision](../decisions/M1_LOCAL_STORAGE_SCOPE.md). Current checks
use its regular-file/stable-folder contract, preserving typed-error/revision
improvements. Prior adversarial evidence remains historical, not a fixed-case
or current acceptance claim. The regression suite is
[test_review_regressions.py](../../tests/contracts/test_review_regressions.py),
with the package-discovery case in
[test_registration.py](../../tests/imports/test_registration.py).
The table records owner verification; it is not an independent approval.

| Finding | Correction / regression |
|---|---|
| F1/F1b: historical OS isolation failure | Earlier rename/swap checks passed, but the final fdce review proved an in-place junction escape. This is not labelled fixed. Explicit human scope now requires stable local folder layout; the special directory-handle layer and two adversarial rename/swap tests are retired. Basic static relative-path/containment checks remain. |
| F2: active result/input linkage | Existing window, segment, generation key, exact global/local ranges/counts/dimensions and canonical useful-media links are checked. Wrong key/window/range/media/geometry reject. Passthrough needs explicit segment selection and matching validated coverage. |
| F3: concurrent newer revision loss | Stage first, then compare current ID/revision under the same OS lease as atomic publication. Original scheduling hook saves revision 3; revision 2 rejects STALE_DEPENDENCY, leaving 3 intact. A post-check competing publication gets retryable PROJECT_BUSY. |
| F4: hidden owned-package ImportError | Explicit lexical child-package imports replace walk_packages' silent omission; broken child returns EXTENSION_IMPORT_ERROR. Optional backends stay lazy. |
| F5: final-newline seed/digest | Complete-string patterns replace permissive `$` endings in runtime/exported schemas. Seed, digest, ID, version and namespace newline cases reject in both validators. |
| F6: bool/number const equality | JSON-aware recursive const/enum equality distinguishes booleans and numbers. Numeric 1 cannot satisfy const true; numeric equality stays numeric. |
| F7: opaque report interpretation | Semantic traversal follows declared schema fields. Finite owner reports remain opaque, including seed/range-like keys; nonfinite JSON still raises INVALID_JSON. No raw ValueError/TypeError. |
| F8: malformed legacy defaults | Shape guard and typed migration handling reject list/text/null/numeric defaults, preserve source bytes and create no destination. |
| F9: incompatible frozen profile | Each frozen window checks selected control/profile links and exact current effective settings. Exclusion returns MODEL_INCOMPATIBLE; a permitted but divergent snapshot returns STALE_DEPENDENCY. |
| F10: raw cyclic-root resolver error | One shared resolver converts native resolution/type failures to PROJECT_IO_ERROR and suppresses path-bearing exception context. Nine initially failing regressions cover cyclic roots in five entry points, cyclic source/destination locators and an invalid root type; originals and folder contents remain unchanged. |
| F11: source-derived FIFO blocking | Reader checks regular-file type before open under stable-layout assumptions. A Windows unit test verifies rejection without opening a synthetic FIFO stat result; a real POSIX FIFO test is present but skipped here. Actual POSIX execution remains NOT PERFORMED. |

The owner preserves the useful local F10 correction while simplifying I/O to
standard Python operations. Fresh normal-use checks cover Unicode/spaces,
explicit overwrite, current/stale revisions, missing/unreadable/malformed
inputs, pre-open type checks, original-preserving migration and injected
ordinary failures. No prior adversarial probe script is rerun under this task.
The new exact committed candidate needs separate review against the revised
contract; owner tests are not source approval or CF acceptance.

The earlier EOF, default/segment control compatibility, selected streams and
per-side context/padding/state-length corrections remain covered. Previously
passing 43/47/83-test suites did not prove OS filesystem isolation.

## Browser check procedure for the next reviewed snapshot

Use a dedicated empty browser workflow; do not replace unsaved human work.
Inspect the connected comfy-mcp catalog and exact four class IDs first. Validate
only the Project UI fixture; do not use validators that load generation models.
The actual runtime workspace is verified privately because a CLI default may
point elsewhere. All operations remain registration/load/serialization only.

The opt-in checker [web/zz_verification.js](../../web/zz_verification.js) is inert
on ordinary pages. At `http://127.0.0.1:8188/?kvd-check=foundation` it loads only
the synthetic four-node/two-link fixture after native initial graph loading.
It requires a completed successful native load, persists EN then RU, compares stable
keys/values/connections and performs native serialize/configure round-trip.
It submits no prompt. Reload with `phase=persist` to check RU persistence and
the saved native graph. `phase=display` loads the fixture for layout inspection.
Capture sanitized EN and RU node-layout screenshots and inspect the actual
console. Pure helper tests or a banner alone do not satisfy appearance review.
Reject actionable errors from this pack; record unrelated pack errors separately.
Restore the prior own language preference, English when initially unset.

Before accepting CF, record actual registration/import, absence of actionable
errors from this pack,
discoverable switch, readable layout and save/reload evidence on the same
reviewed deployed snapshot. Until then these rows stay BLOCKED and downstream
implementation remains gated. Shared-runtime ownership has not been released.

## Integrity and public artifacts

The brief keeps canonical blob `77e34e02374483fc19be006dc5d5b78e40f15042` and
canonical SHA256 `81B86AB34ADD27455F5A6B4F37652050A5DDE0FEEB024F25616FF1D53D6C513B`.
Checkout bytes are checked separately for line-ending preservation. Research
source pins are unchanged. Private session/model/machine/auth evidence and
absolute user asset paths remain in AO. Public fixtures are synthetic metadata;
no media, model weights or generated output is bundled. Project license remains
unselected for this draft; [NOTICES](../../NOTICES.md) records the decision.
