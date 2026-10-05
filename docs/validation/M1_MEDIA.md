# M1-02 isolated CPU media receipt

Original implementation: **cd1b90f5e5d91d9c01d9fd5123dc7a2ab26f81b7**, direct
parent **ac335b87c966b3353c5115c663d4344ff08c01a0**, descendant of accepted C0
**7960568eff779c8c35c3d28a985a243368b91c26**. The explicit
M1-02-INTEGRATE-C923 release integrates the entire checked common
**c923d9e4292ea40e4a3f37f2feace8fa252eecb4** (tree
`7460dfd9b64abeb016029d0d2e6bc191a4acd91d`) with a normal merge of the two
exact heads. The common correction has a separate
[source/synthetic approval](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5415254811).
The normal integration commit is `d0625152a370a6e20e799eb7d6dbaf224c1e252d`
(tree `63e8613d65739ea94226f729157ffc13ba6b447f`). The explicit
M1-02-STREAM-SELECTION-FIX release uses it as the base for one ordinary appended
owned correction, preserving both merge parents and the entire exact c923.
This approval covers the common source, not independent media acceptance,
CI, live CF or H3. PR2 remains draft/unmerged; the foundation live graph/UI gate
remains BLOCKED. The existing
[draft stacked PR3](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/3)
and private AO report identify the frozen output SHA/tree.

M1-02-FIX-R1-R3 starts from exact `d9b3a574dbfdd2bb4ec1428b5d91186fff3e107c`
(tree `313576e588feafb9f3a66f9d6180d4ecce8b890f`). Its independent
[full source/CPU review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/3#pullrequestreview-5416806760)
resolved D1–D4 and requested R1–R3 changes. After local correction authorization,
the coordinator reconciled that completed exact-target provider receipt and
released one normal checked corrective commit/push and existing PR3 update.
The entire checked c923 remains integrated and the PR base remains fixed.
The new candidate's source/test hashes and publication identity are supplied
through AO/PR3. It has owner CPU evidence, with separate reassessment pending.

M1-02-FIX-R4-MONITOR is local preparation from the published R1–R3 correction
`465bc3d91777eb7d5d93b68904df10fdc71910cc` (tree
`56b9c73321b5e6689ab8d83899d45d6edd911357`, direct parent d9b3).
Its completed independent [source/CPU review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/3#pullrequestreview-5417458849)
passes the original R1–R3 probes, retains D1–D4 as resolved and requests only
R4's unwrapped monitor-constructor failure; both constructor/start probe children
already terminate, wait and close. The owner reads the actual private evidence,
reproduces and corrects the error boundary locally. The coordinator reconciled
the completed exact-465 COMMENT/GET/body/postguard receipt, then explicitly
released one normal checked corrective commit/push and existing PR3 body update.
The base and entire integrated common remain c923; this new candidate needs
separate pinned independent review.

Scope: [five unchanged callable signatures and eight real node definitions](../MEDIA_HANDOFF.md).
Runtime is standard-library Python plus explicit existing external executables.
The merge imports foundation-owned changes exactly from c923. No media-owned
changes were made to shared contracts, schemas, package/lockfiles, registry,
common presentation, README/PLAN/INDEX or other task journal. Shared protected
paths match c923. The d062-to-d9b3 correction changed five owned source files,
bounded ordinary tests and this receipt/handoff/card. Owned nodes/presentation are
unchanged from cd1b90. Preparation is1.0.1, assembly is1.0.2 and media binding
is1.0.0; no shared record/schema change was required. The R1–R3 follow-up changes
three owned source files, two new owned test files, one owned audio test file
and the same three owned documents. Recipe/export-policy formats stay1.0.0.
The local R4 diff changes only owned `media/backend.py`, its existing process
regression test and these three existing media documents. Normalization, audio
policy, frontend, ports and dependencies stay unchanged from465.
KVD-WORKER/2.0.0, data/schema2.0.0, five callable signatures, eight owned IDs and
owner recipe/export versions remain stable. The preserved brief still has
Git blob `77e34e02374483fc19be006dc5d5b78e40f15042` and canonical SHA256
`81B86AB34ADD27455F5A6B4F37652050A5DDE0FEEB024F25616FF1D53D6C513B`.

## Actual environment and backend

Checks ran on Windows with isolated Python3.11.6 and verification-only packages
from unchanged `requirements-verify.lock`; Node26.3.0 built-in tools were used.
Both explicitly located executables report **8.0.1-full_build-www.gyan.dev**,
Gyan full build, gcc15.2.0; configuration includes `--enable-gpl --enable-version3`.
Their `-L` metadata declares **GPLv3-or-later**. No binary/source/weights/media are
redistributed. The existing [component/license notice](../../NOTICES.md) remains
unchanged; this task does not select the project's distribution license.
Private paths, machine/session/model/client/auth diagnostics are kept out of this
receipt. Backend version/build-output digests are recorded in operation reports.

## Verification scope and results

Integrated verification commands (after explicit backend selection below):

```text
.venv/Scripts/python.exe -m pytest tests/contracts tests/imports tests/media tests/planning tests/assembly -q -ra -s --tb=short
node tests/ui/presentation.test.mjs
node --experimental-vm-modules tests/ui/language.test.mjs
node --experimental-vm-modules tests/ui/verification.test.mjs
node tests/ui/media.test.mjs
node --experimental-vm-modules tests/ui/media-host.test.mjs
```

Media tests require explicit absolute `KVD_TEST_FFMPEG` and `KVD_TEST_FFPROBE`
environment variables for the reviewed existing executables. They never search
personal folders, download/install a backend, or silently substitute a PATH
build. Missing selection produces clearly labeled backend-dependent skips;
pure planning/import/signature/geometry checks still run. CPU tests call operation
handlers directly. Node definitions are imported/inspected without running a
ComfyUI workflow or queue.

Local R4 corrected source run: **222 passed, 1 skipped, no failures in65.96s**,
both backends explicitly selected. This includes all105 owned
media/planning/assembly cases, the actual4:3 geometry case, shared
contracts/imports/conformance and the existing bounded-memory assertion.
The skipped case is `test_review_regressions.py`'s POSIX FIFO runtime case on
Windows; that platform behavior remains NOT PERFORMED.

Retained frontend results at unchanged source465: shared presentation script
passed; language-setting synthetic
host **6/6**, common verification-checker synthetic host **29/29**, eight owned
EN/RU presentations and owned synthetic-host extension **1/1** passed. The VM
flag was supplied for all module-host tests. Six shared/owned JavaScript source
files passed syntax checks. These are portable/synthetic-host checks; no live
ComfyUI page, graph, serialization or node execution was performed. No frontend
rerun is needed for this backend-only correction; the prior log hashes and
unchanged presentation source are retained in the private local receipt.

The normal d062 integration run recorded161 passed/one POSIX skip/no failures
in32.31s at unchanged media code. The original ac335 owned run recorded44 passed
in31.27s, followed by the expanded
actual4:3 geometry check. Its initially omitted Node VM flag was corrected
without a production fix. Those results remain historical evidence for their
exact sources; the combined run above provides fresh owner correction evidence.
The d9b3 owner run recorded183 passed/one POSIX skip/no failures in50.24s;
the independent review also ran183/one skip and then reproduced R1–R3 with
additional bounded probes. A green suite alone did not establish their absence.
The published R1–R3 owner run recorded217 passed/one POSIX skip/no failures
in66.10s, including100 owned cases; its numeric evidence remains historical
at exact465.

## R4 monitor setup correction

The actual private exact-465 reviewer script/results were available and read;
the owner did not rerun the whole reviewer probe script. The extended process
test uses tiny synthetic FFmpeg media and captures only its own spawned child.
Before the production edit, the six monitor cases recorded **2 failed, 4 passed
in0.40s**. Constructor `RuntimeError` escaped raw with its synthetic message;
constructor `OSError` was redacted as `PROJECT_IO_ERROR` instead of the required
monitor `RESOURCE_LIMIT`. Both child-cleanup assertions passed before the error
assertions failed. Start-phase known failures and unexpected `TypeError` cases
already passed. Fixture cleanup always terminates, waits and closes captured
handles, including on a failed assertion; no unrelated process is accessed.

The production change moves Thread construction inside the existing
`RuntimeError`/`OSError` handler that already covers start. It retains explicit
exception-context suppression and the enclosing mandatory cleanup; no broader
exception catch is added. Four constructor/start known-error cases now produce
redacted `RESOURCE_LIMIT`, including formatted traceback checks. Two unexpected
constructor/start `TypeError` cases preserve the original exception and visible
trace while still cleaning the actual child. The complete focused process set
plus the existing mid-pipe cancellation/quota check records **11 passed in1.95s**.
Invalid limits start zero children, and valid completion/timeout remain checked.
The combined fresh222-pass/one-skip result above protects recipes, selected
streams/bindings, padding, geometry, global PCM and checked export. Backend/API,
algorithm/recipe/policy versions and shared files remain stable. Owner evidence
does not approve this working diff; publication follows the separate coordinator
release after completed exact-465 review reconciliation.

## R1–R3 independent findings and owner correction

The following cases were read from the actual private reviewer script/results,
then reproduced in owned tests before editing production code. The red run
recorded **14 failed, 22 passed in17.51s**. Captured synthetic children were
always terminated/waited/closed in test cleanup, including failures of the
pre-fix implementation. No unrelated process or PID was touched.

| Finding | Owner pre-fix observation | Corrected behavior and focused checks |
| --- | --- | --- |
| R1 | `timeout_seconds='0'` or a nonnumeric limit spawned a running child before typed failure. A monitor-start failure also left the captured child running. | Limits/current budget are checked before spawn; all post-spawn setup is covered by termination/wait/pipe cleanup. Unstarted monitors are not joined. Limit/monitor errors are redacted `RESOURCE_LIMIT` with raw exception context suppressed. Six final focused checks pass in1.68s, including actual valid completion, timeout, cancellation, quota cleanup and traceback redaction. |
| R2 | None/int/bool roots leaked `TypeError`; FPS denominator true and floating24/1 values were accepted by Python equality. | An owned strict recipe schema uses the unchanged shared JSON-aware helper: object/fields/types/fixed values/bounds are checked. Invalid input is typed/redacted; six documented rate/mode combinations remain valid and unmodified. Twenty-two pure checks pass in0.06s; no backend execution is needed. |
| R3 | Six-frame two-scene preserve/mute and preserve/supplied-generate cases without selected source audio required nonexistent global PCM. | Both preserve/mute orders export six video-only frames. Both preserve/generate orders produce exact silence beside supplied PCM (8000samples at32000Hz) and one final encode. Known selected audio missing PCM and absent generated useful PCM still fail. The discontinuous preserve/generate positive probe remains exact4000samples with one reported -1 phase fit. Nine actual synthetic audio checks pass in17.32s. |

Assembly advances to `kvd-assembly/1.0.2` for the corrected audio behavior;
old export artifacts are retained. Canonical recipe values, temporal identity,
stream binding, profile/window/padding policy, node IDs and shared interfaces
remain unchanged. Full results and portable frontend checks are recorded above;
no independent approval of this follow-up is implied.
The first full run passed217/one skip in66.50s. A subsequent traceback regression
found that the monitor wrapper still exposed its underlying error, and a second
case reproduced the same issue in invalid-limit conversion. Both red checks
failed before explicit context suppression; the strengthened six-case R1 set
then passed. Because error behavior changed, that R1–R3 final combined run was
repeated at its exact source/test bytes. Frontend source was unchanged after its passing
run, which was retained rather than repeated for documentation edits.

## Reproduced preliminary findings and corrections

Reviewer6's original-cd1b90 preparation was source-only, with no executed defect
receipt or approval. The owner ran the following bounded actual synthetic
regressions against unchanged relevant code before each correction:

| Finding | Executed pre-fix observation | Corrected behavior |
| --- | --- | --- |
| PREP-D1 | Two same-CFR/geometry video tracks encode different frame numbers. Selected second-track export decoded first-track pixels, including a leading audio track (absolute video indices1/2). Correcting the map then exposed identical export cache paths across selections. | Verified absolute stream is decoded; selected-artifact binding enters assembly identity. Both tracks match independent decoded pixels, use different durable paths and preserve the first export. |
| PREP-D2 | Same-file/equal-PTS video selections were accepted cross-bound in both directions. Correctly bound selections also produced the same Project ID despite different canonical pixels. | Versioned content/MediaRef/absolute-stream/probe binding is recorded and checked in normalization cache and Project construction. Mismatches raise `STALE_DEPENDENCY`; matching selections have distinct Project IDs. |
| PREP-D3 | Fifteen cases across normalization cache, preparation cache and decoded timing: `{}`, list, scalar, malformed nested field or unsupported owner version leaked raw key/type/attribute errors or were accepted. | Required object/field/type/version and existing schema checks occur before consumption. All cases raise redacted `INVALID_RECORD`, preserve every existing fixture byte and create no new artifact/active success. Existing cancellation and manifest size-limit cases retain `CANCELLED`/`RESOURCE_LIMIT`. |
| PREP-D4 | A valid six-useful/native124 window declared tail `repeat_frame=0`, but inverse-cropped output contained118copies of frame5. | M1's documented last-useful-frame boundary policy explicitly rejects the unavailable non-final repeat with `UNSUPPORTED_CAPABILITY` before preparation/cache reuse. No output is created; ordinary last-frame padding still passes. |

Initial stream regression:5 failed in8.06s; map-only follow-up:2 cache-identity
failures in5.25s. Corrected binding/stream focused set:6 passed in8.43s. Initial
envelope/padding set:16 failed/one error-code preservation case passed in11.87s;
corrected envelope set:16 passed in9.23s. Combined affected-file regression:
**33 passed in35.32s**. Final full results are above. These are owner synthetic
CPU receipts; separate review must assess the final exact candidate.

Historical ac335 `tests/imports tests/contracts` run: **97 passed, 1 skipped,
6 failed**. The six failures were the acknowledged shared-test extension dependency:

- `test_import_and_nodes_without_optional_dependencies`: old exact-four-ID
  assertion rejects eight additional real nodes, despite import safety.
- `test_typed_operation_call_examples`: its old unsupported assertion fails for
  each of the five newly registered real operations. Signature/example construction
  and no-I/O portions pass; the other four operations remain unsupported.

Foundation's separately reviewed two-test amendments were imported as part of
the full exact c923 merge. All six formerly failing cases pass in the fresh
combined run. The root test still requires all four foundation IDs and evaluates
every discovered owned `INPUT_TYPES` with optional dependencies absent. All-nine
signature conformance stays independent of handler execution; unsupported
errors are checked against an explicitly empty registry. No test was weakened
or skipped by the media owner. The Windows POSIX skip remains explicit; this
receipt does not claim CI or all-platform acceptance. Owned import tests
deliberately deny optional packages and subprocess creation, import all twelve
actual nodes, evaluate every `INPUT_TYPES`, and verify all five concrete callable
signatures against KVD-WORKER/2.0.0. Actual produced records independently validate
against the existing generated JSON schemas.

| Evidence | Actual checks |
| --- | --- |
| Pure rational/planner | Half-up/minimum-one-frame bounds; absolute Q at 32000Hz; selected coverage; L1/346/360/1000; editorial identities retained; no context/refs |
| Actual decoded source/CFR | 60fps drops; 30000/1001 fractional source; VFR PTS0/4/13/18 at 1/120 with gaps; RGB frame-number identity and selection manifest; decoded target PTS exactly j/24 and EOF F/24 |
| EOF/clamp | Actual one-frame 120fps source: D1/120 → R0/F1/error1/30; missing decoded duration fault injected into real decoder metadata: explicit policy required and recorded |
| Native preparation | Six useful frames → native124 with118 exact last-frame repeats; canvas64×32 for37×19; inverse crop pixel identity; prompt change reuses source/spatial artifact |
| Display geometry | Actual MOV display rotation90 matches independent native displayed decoder; square-pixel4:3 image32×24 preserves pixels; actual SAR4/3 square-pixel output43×24; portrait19×37; pure landscape/4:3/odd/grid transforms |
| Audio | Actual +/-1/12s offsets and impulses; Fs32000 absolute boundaries across native windows; selected range125..471 regression with impulse at technical boundary298 and no accumulated rounding; supplied generated-useful PCM; mute/no selected source audio |
| Assembly/export | Independent synthetic output numbers differ from source; exact useful counts for F1/24/360; missing/extra/changed/false-PTS outputs rejected; odd H.264 reject/explicit pad38×20; actual final decoded video/sample/dimension checks |
| AAC | One final encode; decoded impulse peaks within one sample at0/2000/100000/198000; signaled1024-sample priming; decoded trailing duration within one video frame |
| Storage/resources | Unicode/spaces; missing/changed/nonregular input; actual preflight/mid-pipe cancellation; monitored quota failure removes unpublished output; content-cache/selection-manifest changes detected; measured memory below |

Planner examples (pure checks, not inference):

| Useful length | Balanced useful frames | Native frames, all pads included |
| --- | --- | --- |
| 1 | 1 | 124 |
| 346 | 173,173 | 175,175 |
| 360 | 180,180 | 192,192 |
| 1000 | 334,333,333 | 345,345,345 |

All native lengths satisfy124–345, `5+17*k`, and strict≤15s at24FPS. Normalization
uses measured duration: ordinary D≥1/48 has error≤1/48; minimum-one-frame
0<D<1/48 has error<1/24. Selection discontinuities may fit one PCM sample at the
end of a complete contiguous run; technical windows never reset sample rounding.

## Measured bounded-memory receipt

The numbers below come from the ordinary bounded-memory test in the final
combined suite, using constructed37×19 RGB frame-number sources. No separate
manual experiment was run. The original ac335 numbers remain in the
[pinned d062 receipt](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/blob/d0625152a370a6e20e799eb7d6dbaf224c1e252d/docs/validation/M1_MEDIA.md).
The previous correction's numbers remain in its
[pinned d9b3 receipt](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/blob/d9b3a574dbfdd2bb4ec1428b5d91186fff3e107c/docs/validation/M1_MEDIA.md).
The R1–R3 correction's numbers remain in its
[pinned465 receipt](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/blob/465bc3d91777eb7d5d93b68904df10fdc71910cc/docs/validation/M1_MEDIA.md).
Tracemalloc
starts after fixture generation; measurements include probe/normalize Python
allocations. The watchdog measures only the operation-owned decoder/encoder
children. These small-geometry figures do not predict1080p/H3 memory.

| Frames | Python traced peak bytes | Declared active RGB bytes | Decoder/encoder peak working-set bytes | Known operation disk peak bytes |
| --- | --- | --- | --- | --- |
| 24 | 1160924 | 6327 | 12713984 / 22073344 | 7782 |
| 1000 | 1211228 | 6327 | 28717056 / 22401024 | 352316 |

Python allocation growth was50304 bytes for an additional976 frames; the active
pixel bound stayed6327 bytes. The test checks Python peak<8MiB, larger-source
growth≤1MiB, and observed child peaks<256MiB. PTS and selection size grows on disk.
The production RGB budget does not claim to impose an OS memory cap on external
FFmpeg. Non-Windows child working-set measurement returns null; that path has not
been run here.

## Limits and remaining gates

Only the stated Windows/external8.0.1 backend cases actually ran. Other platforms,
backend versions, large-film throughput, reflected/nonorthogonal transforms,
multichannel audio and live native ComfyUI UI/serialization are unverified or
explicitly unsupported. Preparation uses exact sequential index discard, so long
timeline performance remains a future optimization. Assembly cache identity is
versioned but requested assembly exports are currently re-encoded/re-verified.
The EOF ambiguity test is decoder-metadata fault injection, not a claim of an
actual ambiguous real-world file. Commit-range whitespace, relevant owned
documentation links, canonical brief/source-ledger integrity and public output
privacy checks passed. No shared ComfyUI acceptance allocation was used.

No personal asset was opened/decoded/normalized/copied/uploaded or committed;
no human generated-video output was inspected. No model/inference/H3/VLM/enhancer,
weights/downloads, paid services, runtime deployment/restart or workflow queue was
used. Synthetic CPU records are not H3 evidence. Source review, portable checks,
live UI acceptance and real-video/GPU receipts remain separate gates.
