# M1-03 adapter CPU validation

Evidence boundary: **source/schema, CPU media and constructed decoded RGB/PCM**.
No private source video, generated output, native executor/queue, model load,
live UI, weights, inference or GPU operation occurred. Independent full H3
source review and installed/human acceptance remain pending. Both workflows
are diagnostic, with muted outputs.

The whole independently reviewed media common
`69ed44577550b8545a40cc3209a488d9fcd13fda` is integrated by normal merge
`74eb530c0fd9445a6bfb603a9c9182a982a5781b`, preserving owned 9185151 and
CM69ed parents. Production media/contracts/dependencies and KVD-WORKER/2.0.0 /
data/schema 2.0.0 remain unchanged. [Media review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/3#pullrequestreview-5417990776)
approves that dependency only.

Exact reviewed local media-test amendment88b844 and foundationf231 (including
c08) were then normally merged whole, preserving every parent. Their full SHAs
and merge commits are in [the handoff](../H3_HANDOFF.md). Shared owner content
is included exactly; it was not manually rewritten. Published media/foundation
refs remain69ed/c923. Independent full H3 review still follows this candidate.

The isolated environment retains the unchanged verification lock. No
Torch/Kornia/runtime package was installed. Existing FFmpeg/ffprobe
8.0.1-full_build (GPLv3-or-later) are explicitly selected for bounded synthetic
media I/O; private executable/capture paths and detailed receipts stay in AO.

## Current receipts

| Check | Actual outcome / limit |
| --- | --- |
| Final integrated Python CPU suite | 381 passed, zero failures, two explicit skips in85.22s after both reviewed whole merges and owned widget corrections; prior340PASS/2FAIL/2SKIP preserved below |
| Media/H3 integration regressions | 16 passes: real normalization/preparation, explicit off, exact authored prompt, actual GraphBuilder links, constructed decoded AV, finalization, result selection and export |
| Aggregate control disk budget | One pass: constructed raw RGB plus recipe receipt share the actual reviewed operation quota; these are not Canny contour bytes |
| Both workflow schema preflights | 13 focused passes: actual integrated classes plus immutable32-class capture and PreviewImage supplement; explicit native widget sockets, typed ports and unchanged10/15 preparation /23/43 generation nodes/links |
| Native Canny synthetic contour | **NOT PERFORMED**; isolated environment lacks native Comfy/Torch/Kornia. Opt-in skip is not a fallback/mock contour receipt |
| Native GraphBuilder | Hash-checked actual stdlib-only source `dabb3f75952a1398891ed87ad853d4ea9c929f322ce6997d4ea916adbc2f209d`; no native executor/sampler/model import or call |
| Graph/profile/header checks | Actual links/ports/required parameters, exact prompt/u64 seed, structural off, stale/profile/AdaLN/v1-v2/dtype/malformed-envelope rejection; checkpoint headers and model availability are explicitly synthetic |
| Useful video | Real bounded FFV1 CPU encode/probe/decode; inverse crop and exact useful 24 FPS frames; probe/PTS/fingerprints agree with reviewed media helpers |
| Source/global audio | Original global PCM and nonzero source offset retained byte-for-byte in synthetic export; no audio-guide conditioning |
| Generated audio bridge | Constructed stereo32k PCM on the actual 40Hz/800-sample native grid; useful trim, reported endpoint pad, one resample to Project rate/layout, absolute Q counts and two-window impulse boundary; native Torch AUDIO conversion unperformed |
| Collection/history | Actual reviewed selection, complete Project.media closure, current JSON array, distinct attempt artifact IDs, changed PCM digest, and partial coverage rejection without source fallback |
| EN/RU/frontend | 54 passed, zero failures/skips in484.0403ms; actual shared/owned modules in synthetic hosts, not live H3 UI acceptance |
| Resource metadata | Original 32-class capture and separate PreviewImage supplement hashes checked. Baseline UNET filename absent: honest `MODEL_INCOMPATIBLE` before checkpoint access |
| Installed custom nodes, real workflow/contours/H3/GPU/quality/cancel/VRAM and human result | **NOT PERFORMED / BLOCKED** at separately allocated runtime and human gates |

All checks are owner evidence, not independent adapter approval. Synthetic
decoded finalization records `validation.evidence_kind=cpu_media` and
`gpu=not_performed`; it does not attest H3 sampling. Geometry plumbing may
stub the absent native Canny call and labels that limitation. No contour
accuracy PASS is inferred.

The initial full collection found identical media/adapter test module names;
an owned adapter test-package marker resolves that collision. The first CM69ed
combined run was340PASS/2FAIL/2SKIP in89.08s, plus44frontend passes; the two
failures were unchanged media-owned exact-registry assumptions. That complete
failed outcome stays in its original AO log and is not relabeled green. The
coordinator routed an extension-aware test-only correction to owner8 and
separately reviewed/released exact88b844. Its whole merge resolves the shared
assumptions while retaining required handler/class/port/import checks. No
shared test was disabled or excluded. Pre-CM215-pass/two-skip and42-frontend
receipts remain historical evidence.

Applying the reviewed frontend widget rule adds38 unlinked sockets to the
preparation artifact and77 to the generation artifact. A static before/after
receipt verifies all preexisting inputs, links, IDs, output slots, titles,
positions and widget values are unchanged; the already linked results_json
widget retains its actual link. Tests also reject absent/misnamed/mistyped or
reordered widget inputs. This source-backed modeling is not native workflow
loading or serialization acceptance.

## Integration observations

The 346-frame constructed project plans two 173-useful-frame windows, each
with native length175. Their generated useful mono32k WAVs contain230667 and
230666 samples respectively, matching absolute global boundaries; the second
window records an endpoint fit of-1. Assembly applies no extra phase correction,
retains the impulse at global Q(173), and performs one final encode. A separate
32k-to-48k case retains its expected impulse position. Native length158 produces
210400 native samples and explicitly pads267 useful endpoint samples; this
source-derived quantization is reported rather than hidden.

The retry regression retains both attempts even when video bytes match, while
the current result array selects only the new attempt. The budget regression
rejects a map-plus-receipt quota overflow before the recipe becomes active.
Invalid audio geometry/rate, mismatched global sound decisions, cancellation,
stale keys and incomplete first-window coverage fail with typed errors.

Preparation uses the actual source-only media shape profile with empty model
components/sampling. It has zero H3Profile/checkpoint/expander/sampler ancestry.
The generation artifact preserves the actual missing-baseline resource gate.
Neither JSON has been loaded, queued or accepted by a native frontend;
`test-1.mp4` is only a human-relative configuration value.

## Preliminary review corrections

Static/unexecuted preparation at saved
`0d80cb7b0fe60fa290ec54f22971771b0b6fb345` was not a final verdict.
Actual-module regressions preserve all three corrections:

- H1: identical map content survives mtime changes and locator relocation in
  generation identity; bytes, stream, geometry and implementation revisions
  still invalidate it.
- H2: approved UNET dtype `default` compiles; unapproved `fp8_e4m3fn` is typed
  `MODEL_INCOMPATIBLE` before expansion. No native loader/dtype execution.
- H3: malformed envelope/sections/core revision yield useful redacted
  `MODEL_INCOMPATIBLE` before GraphBuilder/model-provider access.

## Reproduction

Use an existing approved isolated verification environment and unchanged lock.
Set `KVD_FFMPEG`/`KVD_FFPROBE` and `KVD_TEST_FFMPEG`/`KVD_TEST_FFPROBE` to
the same authorized existing binaries. Set `KVD_GRAPH_BUILDER_SOURCE` to the
inspected pinned raw GraphBuilder file. Supply `KVD_NATIVE_SCHEMA_CAPTURE`,
`KVD_PREVIEWIMAGE_SCHEMA_CAPTURE` and `KVD_PREVIEWIMAGE_SCHEMA_RECEIPT` from
the runtime owner's immutable read-only handoffs; the hashes are checked.
Missing artifacts cause explicit skips, without fake installed schemas.

```text
python -m pytest tests/imports tests/contracts tests/media tests/planning tests/assembly tests/controls tests/adapters -q -rs
node --experimental-vm-modules --test tests/ui/*.test.mjs
git diff --check
```

The portable graph fixture declares **synthetic** model availability and must
never be read as installed checkpoint proof. `KVD_RUN_NATIVE_CANNY_CPU=1` is a
separate unexecuted opt-in for an authorized runtime-owner contour check. It is
disabled here; do not install optional packages to make the receipt green.
The Windows-skipped POSIX case is a separate unperformed storage-platform check.

[H3_HANDOFF.md](../H3_HANDOFF.md) describes the two human phases, exact required
model names, original-audio default, partial-window/save/export wiring and
pending resource/runtime gates. The preserved brief and research/license ledger
are untouched. Final source/test/provider receipts are reported privately in AO.
