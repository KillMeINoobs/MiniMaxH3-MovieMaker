# M1-02 isolated CPU media receipt

Implementation source dependency: **ac335b87c966b3353c5115c663d4344ff08c01a0**,
descendant of accepted C0 **7960568eff779c8c35c3d28a985a243368b91c26**.
This is the explicitly released, separately source/CPU-reviewed common commit,
not merged main, accepted full CF or live foundation UI evidence. PR2 remains a
draft dependency; the foundation live graph/UI gate remains BLOCKED.

Scope: [five unchanged operations and eight real node definitions](../MEDIA_HANDOFF.md).
Runtime is standard-library Python plus explicit existing external executables.
No shared contracts, schemas, package/lockfiles, registry, common web files,
README/PLAN/INDEX or other task journal was edited. The preserved brief still has
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

Owned suite command (after explicit backend selection below):

```text
.venv/Scripts/python.exe -m pytest tests/media tests/planning tests/assembly -q -s --tb=short
node tests/ui/media.test.mjs
node --experimental-vm-modules tests/ui/media-host.test.mjs
node --experimental-vm-modules tests/ui/language.test.mjs
```

Media tests require explicit absolute `KVD_TEST_FFMPEG` and `KVD_TEST_FFPROBE`
environment variables for the reviewed existing executables. They never search
personal folders, download/install a backend, or silently substitute a PATH
build. Missing selection produces clearly labeled backend-dependent skips;
pure planning/import/signature/geometry checks still run. CPU tests call operation
handlers directly. Node definitions are imported/inspected without running a
ComfyUI workflow or queue.

Final consolidated owned run: **44 passed in31.27s**, both backends selected,
including the save/replan regression. The expanded actual4:3 geometry case was
then checked separately. Owned presentation check passed for all eight IDs;
owned synthetic-host extension test passed. Existing shared language-setting
synthetic-host tests passed **6/6** with the required Node VM flag (an initial
invocation omitted that flag and was corrected; no production fix was required).

Relevant existing `tests/imports tests/contracts` run: **97 passed, 1 skipped,
6 failed**. The six failures are the acknowledged shared-test extension dependency:

- `test_import_and_nodes_without_optional_dependencies`: old exact-four-ID
  assertion rejects eight additional real nodes, despite import safety.
- `test_typed_operation_call_examples`: its old unsupported assertion fails for
  each of the five newly registered real operations. Signature/example construction
  and no-I/O portions pass; the other four operations remain unsupported.

Foundation owns the two assertion-site amendments. They were not edited here,
and no moving/unreviewed foundation branch was adopted. The full shared suite is
**not green** at this dependency. The existing skipped case is the portable
POSIX-only filesystem case on Windows, not a media PASS. New owned import tests
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

Actual normalization of constructed37×19 RGB frame-number sources. Tracemalloc
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
actual ambiguous real-world file. No shared ComfyUI acceptance allocation was used.

No personal asset was opened/decoded/normalized/copied/uploaded or committed;
no human generated-video output was inspected. No model/inference/H3/VLM/enhancer,
weights/downloads, paid services, runtime deployment/restart or workflow queue was
used. Synthetic CPU records are not H3 evidence. Source review, portable checks,
live UI acceptance and real-video/GPU receipts remain separate gates.
