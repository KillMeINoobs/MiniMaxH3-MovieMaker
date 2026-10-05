# M1-03 adapter CPU validation

Evidence boundary: **source/schema, pure CPU and constructed decoded pixels**.
No original/private video, generated output, model load, queue, live UI, weights,
inference or GPU operation occurred. Final media integration and independent
adapter review remain pending; the workflow is diagnostic.

The owned changes retain exact reviewed whole common
`c923d9e4292ea40e4a3f37f2feace8fa252eecb4` and unchanged KVD-WORKER/2.0.0 /
data/schema 2.0.0 interfaces. The CPU environment uses the existing unchanged
`requirements-verify.lock`; no Torch/Kornia/runtime package was installed.
Existing external FFmpeg/ffprobe 8.0.1-full_build (GPLv3-or-later) were selected
explicitly for bounded constructed-pixel I/O. Their paths stay private in AO.

## Current receipts

| Check | Actual outcome / limit |
| --- | --- |
| Full Python CPU suite | 215 passed, 2 skipped; unchanged shared tests and owned implementation checks |
| Owned controls/adapters | 98 passed, 1 native-Canny skip, included in the full suite |
| Native Canny synthetic contour | **NOT PERFORMED**; isolated environment has no native Comfy/Torch/Kornia. The skipped opt-in case is not a fallback/mock algorithm receipt |
| GraphBuilder source | Actual pinned stdlib-only module SHA256 `dabb3f75952a1398891ed87ad853d4ea9c929f322ce6997d4ea916adbc2f209d` imported from isolated source cache; no native executor/sampler/model imported or called |
| Native graph | Actual GraphBuilder links, seed including u64 max, exact prompt, class/port/slot/enum/schema checks, control-off branch, stale/profile/AdaLN/dtype/malformed-envelope rejection |
| Safetensors | Constructed headers only: observed shape/key/AdaLN/v1/v2 markers, truncated/unknown layout and cancellation errors; no checkpoint/weight test |
| Finalizer | Real CPU FFV1 encode/probe/decode of 192 constructed 32×32 frames, exact 180 useful 24×16 frames, first/last cropped pixels and durable hashes/receipts; stale/count/cancel/quota errors |
| EN/RU/frontend | 42 passed, including six owned module/host-simulation tests, actual shared persisted-language helper readback and owned callbacks; no live browser/layout/serialization acceptance |
| Resource metadata | Actual read-only 32-class schema handoff; initial baseline UNET filename absent, so strict profile preflight fails honestly before any checkpoint access |
| Workflows | 10-node / 15-link preparation-only variant with no H3 generation dependencies, and 22-node / 41-link generation variant; outputs muted, neither loaded/queued. Media interfaces remain pinned dependency descriptions, not code in this checkout |
| Global audio/assembly integration | Pending the explicit reviewed common SHA containing media; local useful-output probe is provisional, generated PCM mode fails explicitly |
| Full foundation, native custom-node installation, real H3/GPU/quality/cancel/memory acceptance | **NOT PERFORMED / BLOCKED** pending separately allocated human/runtime gates |

The constructed-pixel finalizer case proves its actual CPU persistence/geometry
behavior. Its RenderResult keeps `validation.evidence_kind=cpu_media` and
`gpu=not_performed`; an active successful CPU finalization is not H3 acceptance.
Geometry plumbing tests stub the missing native Canny call and are labeled as
such. No contour accuracy PASS is inferred from them.

The preparation-only settings case exercises the actual owned module using a
valid shape-only RenderProfile with empty components/sampling. It passes without
opening an H3 checkpoint. Generation's strict profile/resource checks remain
unchanged. `test-1.mp4` is only a relative human configuration value in the
diagnostic artifact; no worker access/copy/decode/upload occurred.

The actual owned expander wrapper was also called as a pure source compiler
with hash-checked stdlib GraphBuilder and explicitly synthetic declared model
availability. It returned actual native links/expansion plus an honest
`GRAPH_COMPILED` status. No native executor, loader, sampler, tensor or checkpoint
was invoked. Finalizer cache identity excludes graph transport hints while
retaining the actual graph receipt as provenance; its regeneration regression
uses real constructed-pixel CPU I/O.

## Preliminary review corrections

Reviewer preparation inspected exact saved
`0d80cb7b0fe60fa290ec54f22971771b0b6fb345`, with static/unexecuted findings,
not a final candidate verdict. Owned actual-module regressions now verify:

- **H1:** mtime change and ordinary locator relocation with identical map content
  preserve generation identity. Changed bytes or effective selected stream,
  probe/decoder versions change the key. Actual native implementation-version
  identity is retained in the map fingerprint/recipe receipt.
- **H2:** native UNET `default` dtype passes the valid GraphBuilder case;
  an unapproved `fp8_e4m3fn` override fails typed `MODEL_INCOMPATIBLE` before
  native expansion. No loader or dtype conversion was executed.
- **H3:** `{}`, missing runtime core, list/null envelope, wrong schema section
  and null runtime return a useful redacted `MODEL_INCOMPATIBLE` before
  GraphBuilder/model access. The same guard protects profile preparation.

## Reproduction

Use an already approved isolated verification environment and unchanged lock.
Set `KVD_FFMPEG` and `KVD_FFPROBE` to explicitly authorized existing binaries.
Set `KVD_GRAPH_BUILDER_SOURCE` to the inspected pinned raw
`comfy_execution/graph_utils.py` file; its SHA256 is checked before import.
Set `KVD_NATIVE_SCHEMA_CAPTURE` to the actual read-only schema handoff. The
portable graph fixture intentionally declares synthetic baseline availability;
it must never be read as an installed checkpoint receipt. Missing source/capture
inputs cause explicit skips, without a fake GraphBuilder or model fallback.

```text
python -m pytest tests/controls tests/adapters -q
python -m pytest -q
node --experimental-vm-modules --test tests/ui/*.test.mjs
git diff --check
```

`KVD_RUN_NATIVE_CANNY_CPU=1` is a separate **unexecuted opt-in** for a runtime
owner's authorized native CPU contour check. Do not enable it in this worker's
environment or install its packages to make the receipt green. The default
explicit skip remains visible. A shared POSIX-only storage case may skip on
Windows independently; it is not a native Canny result.

No private machine/session/model/auth diagnostics are public. The preserved
brief and research/license ledger remain untouched. Exact final commit/test
receipts and subsequent reviewed media integration will update this document.
