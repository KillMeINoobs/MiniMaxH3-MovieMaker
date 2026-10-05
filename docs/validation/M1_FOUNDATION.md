# M1 foundation validation

Accepted base C0: `7960568eff779c8c35c3d28a985a243368b91c26`, containing M0
final head `9dac703183e3e56929432054f5ebc6d63c26d8e2`. This receipt covers the
M1-01 implementation and review follow-up. Exact pushed candidate and clean-tree
receipts are recorded in AO and [draft PR #2](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2).
It does **not** accept CF; a separate reviewer checks the pinned final candidate.

## Evidence levels

| Check | Result / scope |
|---|---|
| Synthetic Python contracts/import/I/O/conformance | Retained exact-ac335 source/CPU evidence: 103 tests on Windows; one POSIX FIFO test skipped. Unchanged backend suite was not rerun for this checker/shared-test correction. |
| Draft 2020-12 schemas and examples | Retained PASS: 16 exported schemas; 15 synthetic record fixtures. Schema/fixture/declarative bytes remain unchanged. |
| Project serialization/migration | PASS: Unicode/spaces, immutable settings, full u64 seeds, duplicate keys, version/features, explicit migration/source preservation. |
| Ordinary local I/O failures | PASS: read/staging/flush/publication failures preserve old bytes and clean temporary files. A post-publication cleanup error logs a redacted warning and returns the committed save. |
| Concurrent Project API writers | PASS: newer revision remains saved; publish-time lease defers a competing writer with retryable PROJECT_BUSY. |
| Invalid/cyclic path resolution | PASS: save/load/migration/locator/explicit asset checks return redacted PROJECT_IO_ERROR for a cyclic selected root; cyclic migration source/destination paths preserve original bytes. |
| Shared import/conformance amendment | PASS: 29 focused Python tests in the two shared modules; extension-present, missing-foundation-ID, eager-dependency, discovery/duplicate/broken-import and explicitly empty-registry cases. |
| Optional dependencies absent | PASS: subprocess blocks media/model/ComfyUI/schema packages and checks every discovered owned class/INPUT_TYPES. A synthetic added node is accepted; eager dependencies at import or metadata stages reject. |
| Nine downstream callable interfaces | PASS: typed examples bind signatures/types without handler discovery/invocation or I/O. All nine names reject against an explicitly empty registry; discovered guard handlers do not affect call examples. |
| EN/RU selector/helper/checker regressions | Local follow-up PASS: 43 Node checks; presentation invariants, six actual-selector tests and 36 actual-checker tests against synthetic native hosts. New candidate review is pending; these tests do not prove browser appearance/persistence. |
| Frontend syntax | PASS: presentation, verified language helper, extension and opt-in checker parse. |
| Diff/brief/ledger/privacy | Checked before publication; final exact receipts are recorded with the candidate in AO. |
| Live `/object_info` registration | Retained PASS: human-restarted reviewed205 registered four classes; later reviewed c923 has the identical backend. Actual catalog/MCP agree on four classes and metadata. Readonly fixture validation has zero errors and one intentional disconnected-load warning. No live calls occurred during this local diagnostics follow-up. |
| Served own frontend | Retained PASS at deployed c923: six served assets byte-match its approved archive. No restart or deployed patch was used for that refresh. The local diagnostics candidate is not deployed. |
| Ordinary EN/RU selector | PARTIAL browser acceptance at c923: actual selector showed four English/Russian help/status panels, stored RU with status-checked readback, then restored the original explicitly stored EN. Other preferences stayed unchanged. Fresh-client/page-reload RU persistence, full layout and graph invariants remain unaccepted. |
| Actual frontend console/layout | BLOCKED at c923: the first native load fulfilled with `undefined` and ordered correlated completion, then rejected a stable fixture mismatch. Its exact differing field/cause is unknown. Screenshot capture timed out with no image or accepted layout. Historical and foreign/unattributed errors are separate. |
| Native workflow load/save/reload | BLOCKED at c923: one roundtrip attempt failed its first stable projection comparison. No second load, checker retry or persist phase was performed. Four nodes/panels/two links alone do not establish all values, ports, order or custom titles. |
| POSIX local I/O/FIFO runtime | NOT PERFORMED in this Windows session; platform-specific FIFO test is skipped. Windows unit test uses a synthetic nonregular stat result to check rejection before open. |
| CPU media decoding / real user video | NOT PERFORMED by foundation. |
| H3/VLM/enhancer generation / GPU / quality / fit | NOT PERFORMED. No queue submission, model load, weight download or output inspection. |
| CI | No checks registered on the draft PR; no CI PASS. |

Backend rows retain reviewed ac335 evidence. The fresh checker/shared-test
correction ran only the focused Python modules, frontend suite and relevant
integrity checks; it does not claim a new complete backend or POSIX run.

Commands used in the isolated verification environment:

```text
.venv/Scripts/python -m pytest tests/contracts tests/imports -q
# Focused coherent checker/shared-test follow-up:
.venv/Scripts/python -m pytest tests/imports/test_registration.py tests/imports/test_worker_conformance.py -q
node --experimental-vm-modules --test tests/ui/presentation.test.mjs tests/ui/language.test.mjs tests/ui/verification.test.mjs
node --check web/common/presentation.js
node --check web/common/language-settings.js
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
storage assumptions. Its 97 deployment files byte-matched the approved archive
from that commit; Windows line endings were checked against canonical Git blobs
separately.
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

## F12/F13 persistence and final presentation correction

Independent [exact-31 review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5412694609)
requested changes on `31f242a12adf5facb1e5ccba798f1d0c64f1b9da`. Its synthetic
repros use the extracted pinned native void setter. They demonstrate checker
PASS while RU persistence is pending/rejected, an unverified restored claim,
and PASS after a successful reload loses the owned panels. The owner reproduced
those cases without runtime access or modifying reviewer originals. The same
setter misuse was source-derived in the ordinary node selector; the coordinator
included it in this UI outcome before implementation.

The real selector and checker now share an awaited `setSettingValueAsync` call
and status-checked, per-key server readback. Native store writes can resolve
HTTP-error responses or skip unchanged cached values, so their resolved promise
alone is insufficient. Primary [settings](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/scripts/ui/settings.ts),
[store](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/platform/settings/settingStore.ts)
and [API](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/scripts/api.ts)
were checked. Only `KVD.Language` is read/written. Unset (`null`) and its effective
English default remain distinct from explicitly persisted values.

The checker records displayed and verified persisted language separately.
Rejected, pending, malformed or unavailable save/readback cannot produce PASS
or a successful fixture. A restored claim requires an awaited write and matching
readback; failed or unverified recovery is reported explicitly. Every required
load and the final acceptance point check graph/canvas, four owned panels,
semantic data and links before the snapshot is published.

The ordinary selector shows localized saving/error status and actual current
versus observed saved language. It attempts verified recovery after failed
saves, retains SETTINGS_ERROR even when recovery succeeds, and reports unknown
persistence or failed recovery honestly. Six actual-module selector tests cover
default EN, RU/EN success, pending and rejected writes, fulfilled HTTP failure,
unavailable readback and failed recovery; they retain data/custom-title/foreign
node assertions. The checker host models a void setter, a promise setter,
independent server state and controlled deferred/rejected writes. Regression
checks include late panel loss and malformed readback. These are source/CPU
receipts; that changed head needed pinned review. Installed205 remained fixed
during that source correction. The later ac335 deployment/live evidence is
recorded below. GPU/video/POSIX runtime remain NOT PERFORMED.

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

## Reviewed ac335 deployment and bounded live diagnosis

Independent [source/CPU review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5413276074)
approved exact `ac335b87c966b3353c5115c663d4344ff08c01a0`, resolving F12/F13.
Its 100 committed deployment files and six served own assets matched the exact
archive. Eighteen backend/package files remained identical to reviewed205;
the existing running instance and empty queue were retained. Registration is
metadata evidence, not executed node outputs. The F14 settings-store links are
corrected to the verified pinned `src/platform/settings/settingStore.ts` path.

The actual served frontend 1.53.6 load implementation still returns a boolean.
A served installed extension wrapper awaits it and discards that return.
This explains a compatibility risk; the current checker did not log its actual
awaited value/type, so that value remains a source-derived inference. Its FAIL
receipt proves that readiness checks passed and the awaited call fulfilled with
a non-true value. No new null-canvas cause or complete native-load success is
claimed from that observation.

A fresh ordinary dedicated client, with opt-in verification disabled, restored
synthetic Project JSON and RU panels. Its workflow-action control was covered
by a native loading overlay, so a complete ordinary import/export comparison
was unavailable. The ordinary own selector saved RU with server readback and
restored effective EN (the preference was initially unset). Other server
preferences retained their hash. Visible text is partial presentation evidence;
it does not prove unclipped layout or connections. Screenshot capture timed out;
the required panel-visibility recovery remained unavailable. An aborted
navigation is not counted as successful page reload.

The source follow-up observes the documented per-call load/configuration hooks
and actual return/rejection/readiness evidence. A void result alone still fails.
All required hooks must occur once in order for the requested graph, and exact
fixture semantics, canvas and owned panels must pass after each load. Hidden
native aborts, missing/duplicate/reordered hooks, arbitrary non-boolean values,
corrupt data and missing reload panels are negative regressions. A temporary
unique ID in this synthetic fixture's owned metadata binds configuration and
completion to the particular request. It is removed before successful saved
evidence; project JSON, ports, values, links and titles stay unchanged. Stale
metadata and unrelated events cannot complete a pending call. A successful
check alone retains the native serialized synthetic graph. New return/diagnostic
and stale-request regressions first failed against the earlier checker; the
daf57 frontend suite passed 29 checks. Saved graph types/ports/values/links
must match the approved Project fixture before native loading; stale saved
data is rejected without loading other nodes. A stackless native rejection now
produces a truthful FAIL receipt.
These are owner source/CPU results; the new candidate needs separate pinned
review before deployment. Installed ac335 stays fixed and CF remains unaccepted.
No foreign pack/core modification, lifecycle action, node execution or queue
submission occurred.

## F15/F16 bounded failure and reserved metadata correction

Independent [exact-daf review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5414488723)
requested changes on `daf57da38313d43c34e665853f79d33633a3d36f`. Its actual
source/synthetic receipt was read back at the exact commit before publication
of the next owner candidate. The owner reproduced the supplied pending second
load after verified RU, current-marker leak after invalid return, and stale
saved-marker PASS using copies of the private probes with only their result
destination changed; reviewer originals were preserved. Those reproductions
demonstrate defects, not acceptance. Seven actual-checker regression groups
cover the correction; six initially failed on daf57 before the fix.

The requested native load now fails after a 15-second asynchronous deadline,
records pending return state and invalidates its per-call observer. The deadline
is failure-only, not proof of completion, a native cancellation API or a way to
preempt a blocked browser event loop. Failure recovery and final own-key
readback each have a separate 15-second deadline so their pending promises
cannot suppress the FAIL receipt. Restored status requires the existing
supported write/readback proof; timeout/rejection or unavailable readback is
reported as unverified. Late native fulfillment/rejection is handled and
logged separately as unaccepted, with no retry, saved fixture or revived PASS.

Reserved `extra.kvd.verification_load_id` is scrubbed from cloned saved input
before inserting the fresh correlation ID and from serialized output/cache.
Cleanup runs even when native return, lifecycle, graph or presentation checks
throw. Runtime cleanup removes only this call's matching ID, including after
late configuration; it preserves a newer/different ID. Other metadata, custom
titles, values and both links remain intact. A successful persist-phase check
refreshes only its owned synthetic cache with marker-free native serialization.

Fresh owner checks: 36 frontend tests and 29 focused shared import/conformance
tests PASS. Controlled timers/pending promises test failure/recovery bounds,
late fulfillment/rejection, stalled recovery/readback and newer-marker
preservation. Shared tests retain the required foundation subset and all-owned
metadata safety under absent optional packages, separate all-nine signature
examples from handler availability, and test real empty/extension registries
without invoking handlers. The changed candidate needs separate pinned review;
installed ac335 and all live BLOCKED rows remain unchanged. No runtime or media
operation occurred for this correction.

## Browser check procedure for the next reviewed snapshot

Use a dedicated empty browser workflow; do not replace unsaved human work.
Inspect the connected comfy-mcp catalog and exact four class IDs first. Validate
only the Project UI fixture; do not use validators that load generation models.
The actual runtime workspace is verified privately because a CLI default may
point elsewhere. All operations remain registration/load/serialization only.

The opt-in checker [web/zz_verification.js](../../web/zz_verification.js) is inert
on ordinary pages. At `http://127.0.0.1:8188/?kvd-check=foundation` it loads only
the synthetic four-node/two-link fixture after native initial graph loading.
It requires correlated native load/configuration completion and exact graph
assertions, records return/type/stack evidence, persists EN then RU, compares stable
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
runtime/browser acceptance remains gated. The coordinator separately released
M1-02 and M1-03 CPU-only source work on each assignment's exact reviewed checked
common base. Their implementation/review does not accept CF, allocate the shared
runtime or establish native H3/GPU execution. Shared-runtime ownership has not
been released.

## Failure-time diagnostics: local follow-up from c923

Exact c923 (`c923d9e4292ea40e4a3f37f2feace8fa252eecb4`) received independent
source/synthetic approval and was deployed for the one bounded live attempt.
The saved FAIL receipt contains lifecycle/identity/return evidence but no actual
failed stable projection. All three observed Project JSON widget values match
the fixture exactly; that does not establish every projected field. No native,
own-presentation or foreign-hook cause is inferred.

The local checker amendment captures complete expected/actual stable
projections and `first_difference` at the existing failed comparison, tied to
its stage and native load ID when applicable. Paths use bracket JSON notation;
both sides include `present`, JSON `type` and the exact `value` when present.
Missing fields/indices, null, type/value changes and object-key order remain
distinct. The same untruncated JSON strings still decide equality; labels,
titles and layout remain outside that projection, with titles checked separately.

The complete diagnostic envelope has a 262,144-code-unit budget. Excess size or
capture failure reports unavailable evidence, preserves the original mismatch
error and does not emit partial projections or a claimed first difference.
Unavailable error formatting is guarded and limited to 1,024 code units,
with explicit truncation status and a budget check of the entire envelope.
If that metadata cannot be represented within budget, a small fixed unavailable
receipt is used. Focused red-to-green tests reproduce the source-preparation
finding PREP-DIAG1: overlong and unprintable diagnostic errors previously escaped
that bound or replaced the original mismatch. Both now retain the original
FAIL/cleanup and verified recovery after RU. A dedicated opaque-JSON test also
retains the original comparator's object-key-order rejection.
Earlier native serialization errors likewise retain their original error.
Cleanup, deadlines, verified preference recovery and all failure/PASS criteria
are unchanged. The new actual-module synthetic cases cover values, ports,
links, identity, absent fields/indices, deterministic first-path order, cosmetic
invariance, post-RU recovery, unavailable/budgeted capture and original-error
preservation. The 43 frontend tests pass locally; eight focused
registration/import checks from the initial local preparation are retained.
Unchanged backend/I/O suites were not rerun. That exact local c08 candidate later
received independent source/synthetic approval and a separate deployment/live
diagnostic release. The resulting failed projections are recorded below; approval
of diagnostics did not supply corrected live acceptance.

## Six native widget inputs: captured failure and local correction

The one c08 browser attempt captured complete expected/actual stable projections
before the same strict comparison rejected them. Input counts were `[0,1,1,0]`
in the authored fixture and `[1,1,4,2]` in the configured graph. The entire stable
diff consists of six additional unlinked primitive widget sockets: Project JSON's
`project_json`, Save's `project_root`, `project_file`, `overwrite` after its linked
`project` slot, and Load's `project_root`, `project_file`. Types are STRING except
BOOLEAN `overwrite`. Every other stable value/type/ID/output/link and key order
was unchanged; the authored Project JSON remains 8,246 characters with SHA256
`31cf8081df848c552ca70bd6130246697548ddc498b068500143c4fc1d82ea09`.
The exact runtime field writer remains unknown. No data corruption is inferred.

The registered class metadata and pinned frontend 1.53.6
[input construction/configuration](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/services/litegraphService.ts)
and [input serialization](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.53.6/src/lib/litegraph/src/node/slotUtils.ts)
support explicit name/type/null-link/widget-name records. Both committed fixture
copies now contain only those six additions. The checker and its full stable
projection/equality, setting readback/recovery, panels, titles, failure deadlines
and marker cleanup are unchanged.

The focused actual-module regression first reproduced the omitted-port FAIL in
a synthetic host driven by independently recorded class input definitions. It
checks explicit `[1,1,4,2]` ports, ordering, widget associations, idempotent first
and second materialization and matching fixture copies. Omitted/changed/missing/
extra ports, type/link/widget-value/ProjectJSON/ID mutations still reject without
a saved acceptance fixture. This source-supported model is not an executed native
regression. All 46 owned frontend tests pass, including the three focused native
widget-input groups; the initial red run had one expected fixture failure and two
passing rejection groups. JavaScript syntax passes. These are owner synthetic
receipts; an independent exact review remains pending.
Backend/Python/media checks retain their previous receipts and are not rerun here.

Actual c08 registration and ordinary EN/RU/EN selector readback/restoration remain
separate evidence. Four selectors/group captions and three help/status blocks
were observed; the fourth help/status is NOT OBSERVED. Screenshot error 10060
produced no image. No successful graph roundtrip, fresh-page RU persistence,
complete layout or CF acceptance exists. Installed c08 and published c923 refs
remain fixed during this local correction. No new live attempt/deployment,
generation, model load, native contour, real-video or GPU execution occurred.

## Integrity and public artifacts

The brief keeps canonical blob `77e34e02374483fc19be006dc5d5b78e40f15042` and
canonical SHA256 `81B86AB34ADD27455F5A6B4F37652050A5DDE0FEEB024F25616FF1D53D6C513B`.
Checkout bytes are checked separately for line-ending preservation. Research
source pins are unchanged. Private session/model/machine/auth evidence and
absolute user asset paths remain in AO. Public fixtures are synthetic metadata;
no media, model weights or generated output is bundled. Project license remains
unselected for this draft; [NOTICES](../../NOTICES.md) records the decision.
