# M1 foundation validation

Accepted base C0: `7960568eff779c8c35c3d28a985a243368b91c26`, containing M0
final head `9dac703183e3e56929432054f5ebc6d63c26d8e2`. This receipt covers the
M1-01 implementation and review follow-up. Exact pushed candidate and clean-tree
receipts are recorded in AO and [draft PR #2](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2).
It does **not** accept CF; a separate reviewer checks the pinned final candidate.

## Evidence levels

| Check | Result / scope |
|---|---|
| Synthetic Python contracts/import/I/O/conformance | PASS: 83 tests on Windows; no failures/skips. |
| Draft 2020-12 schemas and examples | PASS: 16 exported schemas; 15 synthetic record fixtures; schema bytes match declarative source. |
| Project serialization/migration | PASS: Unicode/spaces, immutable settings, full u64 seeds, duplicate keys, version/features, explicit migration/source preservation. |
| Actual Windows filesystem races | PASS: parent replacement denied during staging and publication; outside folder stays empty; original bytes survive failure. |
| Concurrent Project API writers | PASS: newer revision remains saved; publish-time lease defers a competing writer with retryable PROJECT_BUSY. |
| Optional dependencies absent | PASS: subprocess blocks media/model/ComfyUI/schema packages; four Project classes still import and expose inputs. |
| Nine downstream callable interfaces | PASS: typed examples bind actual signatures; every unimplemented operation rejects registry dispatch; no handler invoked. |
| EN/RU helper invariants | PASS: one Node test file asserts English default, translated labels/errors, unchanged keys/values/links, custom titles and foreign-node preservation. |
| Frontend syntax | PASS: shared presentation, extension and opt-in checker parse. |
| Diff/brief/ledger/privacy | Checked before publication; final exact receipts are recorded with the candidate in AO. |
| Live `/object_info` registration | BLOCKED: deterministic old package staged, supported existing Desktop restart unavailable to automation. No registration PASS claimed. |
| Actual frontend import/console/layout | BLOCKED: requires that restart and registered nodes. No EN/RU screenshots or console PASS claimed. |
| Language persistence + native workflow save/reload | BLOCKED in actual browser; pure helper checks are not a browser receipt. |
| POSIX protected I/O runtime | NOT PERFORMED in this Windows session; implementation uses dir_fd/O_NOFOLLOW. |
| CPU media decoding / real user video | NOT PERFORMED by foundation. |
| H3/VLM/enhancer generation / GPU / quality / fit | NOT PERFORMED. No queue submission, model load, weight download or output inspection. |
| CI | No checks registered on the draft PR; no CI PASS. |

Commands used in the isolated verification environment:

```text
.venv/Scripts/python -m pytest tests/contracts tests/imports -q
node --test tests/ui/presentation.test.mjs
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

## Independent review findings and owner regressions

The independent review requested changes on `260a37dadc04477d1d0779f188ffaf5ebff0c35b`.
The owner reproduced failures before fixes. The regression suite is
[test_review_regressions.py](../../tests/contracts/test_review_regressions.py),
with the package-discovery case in
[test_registration.py](../../tests/imports/test_registration.py).
The table records owner verification; it is not an independent approval.

| Finding | Correction / regression |
|---|---|
| F1: parent-swap write escape | Windows FILE_LIST_DIRECTORY handles deny delete sharing across every component through staging/publication. Original NamedTemporaryFile swap fails with typed PROJECT_IO_ERROR before an outside write; late publish swap preserves original. Metadata-only handles were experimentally insufficient and are not used. |
| F2: active result/input linkage | Existing window, segment, generation key, exact global/local ranges/counts/dimensions and canonical useful-media links are checked. Wrong key/window/range/media/geometry reject. Passthrough needs explicit segment selection and matching validated coverage. |
| F3: concurrent newer revision loss | Stage first, then compare current ID/revision under the same OS lease as atomic publication. Original scheduling hook saves revision 3; revision 2 rejects STALE_DEPENDENCY, leaving 3 intact. A post-check competing publication gets retryable PROJECT_BUSY. |
| F4: hidden owned-package ImportError | Explicit lexical child-package imports replace walk_packages' silent omission; broken child returns EXTENSION_IMPORT_ERROR. Optional backends stay lazy. |
| F5: final-newline seed/digest | Complete-string patterns replace permissive `$` endings in runtime/exported schemas. Seed, digest, ID, version and namespace newline cases reject in both validators. |
| F6: bool/number const equality | JSON-aware recursive const/enum equality distinguishes booleans and numbers. Numeric 1 cannot satisfy const true; numeric equality stays numeric. |
| F7: opaque report interpretation | Semantic traversal follows declared schema fields. Finite owner reports remain opaque, including seed/range-like keys; nonfinite JSON still raises INVALID_JSON. No raw ValueError/TypeError. |
| F8: malformed legacy defaults | Shape guard and typed migration handling reject list/text/null/numeric defaults, preserve source bytes and create no destination. |
| F9: incompatible frozen profile | Each frozen window checks selected control/profile links and exact current effective settings. Exclusion returns MODEL_INCOMPATIBLE; a permitted but divergent snapshot returns STALE_DEPENDENCY. |

The earlier EOF, default/segment control compatibility, selected streams and
per-side context/padding/state-length corrections remain covered. Previously
passing 43/47-test suites did not prove the later race/linkage guarantees.

## Browser check procedure after the human restart

Use a dedicated empty browser workflow; do not replace unsaved human work.
Inspect the connected comfy-mcp catalog and exact four class IDs first. Validate
only the Project UI fixture; do not use validators that load generation models.
The actual runtime workspace is verified privately because a CLI default may
point elsewhere. All operations remain registration/load/serialization only.

The opt-in checker [web/zz_verification.js](../../web/zz_verification.js) is inert
on ordinary pages. At `http://127.0.0.1:8188/?kvd-check=foundation` it loads only
the synthetic four-node/two-link fixture, persists EN then RU, compares stable
keys/values/connections and performs native serialize/configure round-trip.
It submits no prompt. Reload with `phase=persist` to check RU persistence and
the saved native graph. `phase=display` loads the fixture for layout inspection.
Capture sanitized EN and RU node-layout screenshots and inspect the actual
console. Pure helper tests or a banner alone do not satisfy appearance review.
Restore the English preference after verification.

Before accepting CF, record actual registration/import, clean console,
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
