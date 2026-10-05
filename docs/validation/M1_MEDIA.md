# M1-02 isolated CPU media receipt

Original implementation: **cd1b90f5e5d91d9c01d9fd5123dc7a2ab26f81b7**, direct
parent **ac335b87c966b3353c5115c663d4344ff08c01a0**, descendant of accepted C0
**7960568eff779c8c35c3d28a985a243368b91c26**. The explicit
M1-02-INTEGRATE-C923 release integrates the entire checked common
**c923d9e4292ea40e4a3f37f2feace8fa252eecb4** (tree
`7460dfd9b64abeb016029d0d2e6bc191a4acd91d`) with a normal merge of the two
exact heads. The common correction has a separate
[source/synthetic approval](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5415254811).
This approval covers the common source, not independent media acceptance,
CI, live CF or H3. PR2 remains draft/unmerged; the foundation live graph/UI gate
remains BLOCKED. The existing
[draft stacked PR3](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/3)
and private AO report identify the frozen output SHA/tree.

Scope: [five unchanged operations and eight real node definitions](../MEDIA_HANDOFF.md).
Runtime is standard-library Python plus explicit existing external executables.
The merge imports foundation-owned changes exactly from c923. No media-owned
changes were made to shared contracts, schemas, package/lockfiles, registry,
common presentation, README/PLAN/INDEX or other task journal. Shared protected
paths match c923; media implementation, tests and presentation match cd1b90.
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
.venv/Scripts/python.exe -m pytest tests/contracts tests/imports tests/media tests/planning tests/assembly -q -ra --tb=short
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

Fresh integrated run on the merged source tree: **161 passed, 1 skipped,
no failures in32.31s**, both backends explicitly selected. This includes all44
owned media/planning/assembly cases, the actual4:3 geometry case, shared
contracts/imports/conformance and the existing bounded-memory assertion.
The skipped case is `test_review_regressions.py`'s POSIX FIFO runtime case on
Windows; that platform behavior remains NOT PERFORMED.

Frontend results: shared presentation script passed; language-setting synthetic
host **6/6**, common verification-checker synthetic host **29/29**, eight owned
EN/RU presentations and owned synthetic-host extension **1/1** passed. The VM
flag was supplied for all module-host tests. Six shared/owned JavaScript source
files passed syntax checks. These are portable/synthetic-host checks; no live
ComfyUI page, graph, serialization or node execution was performed.

The original ac335 owned run recorded44 passed in31.27s, followed by the expanded
actual4:3 geometry check. Its initially omitted Node VM flag was corrected
without a production fix. Those historical receipts remain valid at unchanged
media source; the combined run above is the fresh integration result.

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

The numbers below retain the original ac335 measurement of constructed37×19
RGB frame-number sources. Media/backend/test source is unchanged from cd1b90;
the integrated suite reran the existing assertion once, with no additional
manual memory experiment. Tracemalloc
starts after fixture generation; measurements include probe/normalize Python
allocations. The watchdog measures only the operation-owned decoder/encoder
children. These small-geometry figures do not predict1080p/H3 memory.

| Frames | Python traced peak bytes | Declared active RGB bytes | Decoder/encoder peak working-set bytes | Known operation disk peak bytes |
| --- | --- | --- | --- | --- |
| 24 | 1148921 | 6327 | 27480064 / 16179200 | 7782 |
| 1000 | 1223633 | 6327 | 28680192 / 22364160 | 352316 |

Python allocation growth was74712 bytes for an additional976 frames; the active
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
