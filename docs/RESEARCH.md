# M0 primary-source audit — V2V revision

Re-inspected **2026-10-04 UTC / 2026-10-05 Europe/Moscow** for [the superseding V2V direction](PRODUCT_DIRECTION_V2V.md). Only selected source/docs/JSON, one UI screenshot and repository/model metadata were fetched. No clone, weights, install, remote-code execution, ComfyUI change, inference, user-asset access or upload. **GPU NOT PERFORMED.**

Evidence labels: **F** direct source fact; **I** inference; **P** project proposal; **U** unknown; **R** independently observed runtime result. There are no H3 R results in M0. Publisher examples/performance statements are not our receipts.

## Source ledger

These are inspected snapshots, not instructions to update the user's installation. Path lists delimit inspection scope. GitHub metadata and license openings were inspected; a license identifier does not decide this project's eventual license. Links use full revisions except the explicitly unversioned FFmpeg publications.

| ID | Source and full revision | Upstream commit/model date (UTC) | Selected paths inspected | License |
|---|---|---|---|---|
| S01 | [ComfyUI core](https://github.com/Comfy-Org/ComfyUI/tree/b87fe48b0491425f682f7ffdaed56d0387cb6c5d), `b87fe48b0491425f682f7ffdaed56d0387cb6c5d` | 2026-10-04 19:06:36 | `comfy_extras/nodes_minimax_h3.py`, `nodes_model_patch.py`; `comfy/ldm/minimax/controlnet.py`, `model.py`, `vae.py`; `comfy/text_encoders/minimax.py` | [LICENSE](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/LICENSE), GPL-3.0 |
| S02 | Same core revision/date | Same | `execution.py`, `server.py`, `comfy_execution/graph_utils.py`, `comfy/model_management.py`, `comfy/utils.py` | Same core license |
| S03 | Same core revision/date | Same | `comfy_extras/nodes_canny.py`, `nodes_video.py`; targeted H3 search in `comfy/controlnet.py`; `requirements.txt` for frontend declaration | Same core license |
| S04 | [Native template](https://github.com/Comfy-Org/workflow_templates/blob/0e5c5efb32ba6f3365d6da07da64aaf668157042/templates/video_minimax_h3_fun_controlnet_union.json), `0e5c5efb32ba6f3365d6da07da64aaf668157042` | 2026-10-02 19:28:52 | `templates/video_minimax_h3_fun_controlnet_union.json`, top-level nodes/links/widgets/model metadata and pose subgraph | [LICENSE](https://github.com/Comfy-Org/workflow_templates/blob/0e5c5efb32ba6f3365d6da07da64aaf668157042/LICENSE), MIT |
| S05 | [Comfy docs](https://github.com/Comfy-Org/docs/tree/9e719d0894db9f90a9056e602a09cfe6a2af3a32), `9e719d0894db9f90a9056e602a09cfe6a2af3a32` | 2026-10-04 21:07:06 | `custom-nodes/backend/expansion.mdx`, `custom-nodes/js/javascript_overview.mdx`, `tutorials/video/minimax/minimax-h3.mdx`, `minimax-h3-fun-controlnet.mdx` | [LICENSE](https://github.com/Comfy-Org/docs/blob/9e719d0894db9f90a9056e602a09cfe6a2af3a32/LICENSE), GPL-3.0 |
| S06 | [MiniMaxAI base card](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/42ed227ee7df40d41602854ae760620d6eb651fe/README.md), `42ed227ee7df40d41602854ae760620d6eb651fe` | lastModified 2026-08-13 01:46:29 | `README.md`, file-list metadata, `LICENSE` | [Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/42ed227ee7df40d41602854ae760620d6eb651fe/LICENSE); HF identifier `other` |
| S07 | [Union v1 card](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union/blob/9df91437f0890b20f8a0b07c1d9500648cfcbf44/README.md), `9df91437f0890b20f8a0b07c1d9500648cfcbf44` | lastModified 2026-09-22 10:13:54 | `README.md`, `LICENSE` | [Community License](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union/blob/9df91437f0890b20f8a0b07c1d9500648cfcbf44/LICENSE) |
| S08 | [Union 2.0 card](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union-2.0/blob/7d2c95de2e351ed6a0b360af45f62daa04c26f88/README.md), `7d2c95de2e351ed6a0b360af45f62daa04c26f88` | lastModified 2026-09-22 09:57:14 | `README.md`, `LICENSE` | [Community License](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union-2.0/blob/7d2c95de2e351ed6a0b360af45f62daa04c26f88/LICENSE) |
| S09 | [Comfy model card](https://huggingface.co/Comfy-Org/MiniMax-H3/blob/e5eb578a89295337b8ff433a035929ce0279e0b6/README.md), `e5eb578a89295337b8ff433a035929ce0279e0b6` | lastModified 2026-09-29 11:11:09 | `README.md`, HF file-list metadata including distinct Union 2.0 conversions | Card links S06 license; quantizer/conversion origins also recorded by publisher |
| S10 | [VideoX-Fun](https://github.com/aigc-apps/VideoX-Fun/tree/4b7b6402a1e0f0406bd6801fb66c0a00bd922621), `4b7b6402a1e0f0406bd6801fb66c0a00bd922621` | 2026-09-29 11:18:17 | `examples/minimax_h3_fun/predict_v2v_control.py`, `config/minimax_h3/minimax_h3_control.yaml`, `minimax_h3_control_inpaint_post_norm.yaml` | [LICENSE](https://github.com/aigc-apps/VideoX-Fun/blob/4b7b6402a1e0f0406bd6801fb66c0a00bd922621/LICENSE), Apache-2.0 |
| S11 | [AIMixer Director](https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director/tree/a8f57b8e23c46ee28fdb96796510fa7b4f3b1fbb), `a8f57b8e23c46ee28fdb96796510fa7b4f3b1fbb` | 2026-09-30 07:17:06 | `README.md`, `nodes/director.py`, `director/segment_runtime.py`, `LICENSE` | Apache-2.0 |
| S12 | [Songssx TimelineDirector](https://github.com/Songssx/ComfyUI-MiniMaxH3-TimelineDirector/tree/a81f13b8af4a162467cec4dc377f40b7354d7ffc), `a81f13b8af4a162467cec4dc377f40b7354d7ffc` | 2026-09-22 13:44:06 | `README.md`, `minimax_h3_finite_segments.py`, `LICENSE` | GPL-3.0 |
| S13 | [DaSiWa Nodes](https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes/tree/afd009473efa1ccff88fa41c557dce94ad9195c3), `afd009473efa1ccff88fa41c557dce94ad9195c3` | 2026-10-04 12:12:41 | `README.md`, `nodes/nodes_minimax_h3_director.py`, `nodes/helper_pyav_video.py`, `LICENSE` | GPL-3.0 |
| S14 | [VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite/tree/4d907bee61e92c2e65af3bd6383a4e4d356126d1), `4d907bee61e92c2e65af3bd6383a4e4d356126d1` | 2026-09-02 06:48:06 | `README.md`, `videohelpersuite/load_video_nodes.py`, `LICENSE` | GPL-3.0 |
| S15 | [ReShot](https://github.com/maosika-ai/ComfyUI-ReShot/tree/3575e39e463cc41588e3f1ef3daa3e15c768d78e), `3575e39e463cc41588e3f1ef3daa3e15c768d78e` | 2026-09-13 18:29:22 | `README.md`, `nodes.py`, `LICENSE` | Apache-2.0 |
| S16 | FFmpeg published docs, unversioned, retrieved 2026-10-04 UTC | Publication revision unavailable; no installed binary inspected | [fps/trim/atrim filters](https://ffmpeg.org/ffmpeg-filters.html#fps), [ffprobe](https://ffmpeg.org/ffprobe.html), [timestamp/fps_mode options](https://ffmpeg.org/ffmpeg.html#Advanced-options) | [Legal page](https://ffmpeg.org/legal.html): LGPL-2.1-or-later, optional GPL parts change effective license; future binary/build remains unknown |

Selected directory listings located these files; no claim covers an uninspected repository wholesale. The ledger is the source key for the tables below.

## Constraints

| Concern | Evidence and distinction | Project consequence / unknown |
|---|---|---|
| Lattice / FPS | **F:** [native H3 node](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/comfy_extras/nodes_minimax_h3.py#L30) increments until `N%17==5`; FPS=24; video latent length `5*k+2`. VAE has 17-frame chunks (S01). | **I:** hypothesis confirmed for this pin; not a universal future preset. |
| Minimum / trained range | **F:** widgets permit 5–3600 before alignment; tooltip says approximately 124–362 trained range. S06 product guidance says 4–15 s. S05 calls 124 frames “5 seconds.” | **P:** recipe floor 124 inference frames for M1, pad short useful clips. 124/24=5.1667 s. Shape minimum 5 is not a quality guarantee; product guidance is not a native hard minimum. |
| Strict maximum | **I:** intersect `N<=360` with the lattice → **345** (14.375 s); next count 362 is 15.0833 s. Native accepts longer than our policy. | **P:** count padding/context before submission; preserve 360 useful frames across multiple windows, never silently truncate or submit 362. |
| Alternative pipeline | **F:** [VideoX example](https://github.com/aigc-apps/VideoX-Fun/blob/4b7b6402a1e0f0406bd6801fb66c0a00bd922621/examples/minimax_h3_fun/predict_v2v_control.py#L254) rounds actual control length downward. Native target rounds upward and short control repeats its tail (S01). | **P:** send exact planned batches; neither implicit rule is our coverage planner. |
| Grid / area | **F:** native dimension widgets step 32, VAE /16 and 2×2 transformer patch. Native `adapt_canvas` helper and S05 describe 768 short edge / 768×1344 preferred area. | **P:** enforce `%32==0`. Preferred/training area is not proof of a hard runtime maximum for direct callers. Larger source sizes need explicit resource warning; Draft scaling is opt-in. |
| Aspect / rotation / SAR | **F:** S06 lists varied aspect ratios. Native control fit uses bilinear center geometry. | **P:** bake display orientation/pixel aspect; one declared fit-and-pad transform shared by RGB/control/masks/results; remove service padding. No silent crop/stretch. |
| Real normalization | **F:** S16 fps filter drops/duplicates by time; ffprobe exposes decoded frames/packets. S03 CreateVideo assigns rate to an existing frame batch. | **P:** measure actual PTS after resampling. Export-rate metadata alone does not normalize VFR/fractional input. |
| Structural role | **F:** native `control_video` is VAE-encoded for the control model patch, not auto-connected as a reference. | **P:** maps only at that socket; RGB used for preparation/extraction only. |
| Inpaint role | **F:** `source_video` consumed only with mask; mask 1=repaint. v2 normalization mode depends on metadata. | **P:** both sockets absent in M1. |
| Appearance role | **F:** native Ref2VA feeds reference frames to Qwen and optionally reference latent blocks; paired audio is reference conditioning. | **P:** references empty for first VID2VA. Preserve source audio only at assembly. |
| Schedule | **F:** [native apply](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/comfy_extras/nodes_minimax_h3.py#L603) maps percentages to sigma then compares sampler sigma. | **P:** denoising bounds, never source seconds; integer source intervals are separate. |
| Audio | **F:** S06 output 32 kHz stereo; joint native AV latents have 40 Hz audio latent rate; control skips zero audio positions. | **P:** preserve/generate/mute are timeline/export choices. Preserve/mute do not stop joint audio inference or promise lip sync. Sample rounding/codec delay need media evidence. |
| Resource fit | **F:** full-precision VideoX memory notes are large; native template uses compressed/pruned files (S04/S07/S08/S09). | **U:** no measured 16 GB VRAM/32 GB RAM fit, speed or peaks for this paired profile. File size and unrelated benchmarks are insufficient. |

## Native workflow and compatibility

S04 loads `minimax_h3_ref2va_pruned_int8_convrot.safetensors`; CLIP type `minimax` with `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`; `minimax_h3_video_vae_int8_convrot.safetensors`; `minimax_h3_audio_vae_fp32.safetensors`. `ModelPatchLoader` loads original `minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors`. It uses `MiniMaxH3FunControlNetApply`, BasicGuider, res_multistep/simple, 20 default steps, AV decode and CreateVideo at 24 FPS. Reference sockets, mask and source_video are unconnected. The producer is an SDPose subgraph. **P:** swap it for prepared Canny, keep references/turbo off.

Node property strings such as 0.33.0 and older subgraph versions are serialization metadata, not a verified minimum runtime. [Pinned control tutorial](https://github.com/Comfy-Org/docs/blob/9e719d0894db9f90a9056e602a09cfe6a2af3a32/tutorials/video/minimax/minimax-h3-fun-controlnet.mdx) specifies **0.35.0+** and both base families. Preflight actual node schemas/loader instead of accepting a version alone.

| Pair | Matching source evidence | Judgment |
|---|---|---|
| Ref2VA + original converted Union | S04 explicit wiring, S05 documentation | Source-supported first recipe if exact compatible installed files exist; no runtime receipt |
| FL2VA + original Union | S05 says both transformer families work | Documented alternative; test separately. VID2VA is not a third checkpoint |
| Union v1 / v2 original layouts | S07 five blocks at 0/10/20/30/40; S08 ten at 0/5/…/45 plus post_norm; 49 control input channels, video-only conditioning | Distinct profiles. v1 VideoX config against v2 can silently drop weights; no name-based substitution |
| Native loader + converted v2 | [Loader](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/comfy_extras/nodes_model_patch.py#L306) counts blocks, derives/validates injection metadata and reads post_norm; [native control](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/comfy/ldm/minimax/controlnet.py#L46) checks AdaLN form. S09 metadata lists separate `union_2.0_pruned_bf16` and `union_2.0_pruned_int8_convrot` files | **I:** structural accommodation for ten blocks. **U:** actual keys/metadata/matched base/loading/output not tested; not guaranteed drop-in |
| Original HF/Diffusers layout → native loader | S06/S10 distribution differs from S09 conversions; native requires internal state-dict keys | Raw originals not proven interchangeable; no automatic conversion/fallback |
| Quantization / kernels | S09 recommends int8-convrot with PyTorch cu130; S05 warns Comfy Kitchen attention with those checkpoints | Include runtime/backend in profile. Installed environment unknown; no M0 modifications |

| Requested control | Union v1 (S07) | Union 2.0 (S08) | Project disposition |
|---|---|---|---|
| Canny | Listed | Listed | M1 mandatory; control-off comparison |
| Depth | Listed | Listed | Later; temporally coherent backend/normalization needs validation |
| Pose | Listed | Listed (DWPose recipe) | Later; native SDPose template is source recipe evidence only |
| Gray | Not listed | Listed luminance video | v2 candidate, not RGB appearance reference |
| Canny+Depth | No combined recipe inspected | No combined recipe inspected | **U**, reject in first capability; no promised map blending/patch stacking |
| Depth+Pose | No combined recipe inspected | No combined recipe inspected | **U**, same gate |
| HED / MLSD | Listed | Listed | Outside M1/M2 |
| Scribble / Layout | Not listed | Listed; Layout has specific VACE recipe | Optional later research, no MVP dependencies |

Ordinary IMAGE input and the word Union do not establish arbitrary combinations. Original Union is marked legacy and its publisher recommends v2; changing our baseline still needs matched loader/weights and a real test.

## Execution and memory

**F:** [expansion docs](https://github.com/Comfy-Org/docs/blob/9e719d0894db9f90a9056e602a09cfe6a2af3a32/custom-nodes/backend/expansion.mdx) specify result links/subgraph, deterministic unique IDs and link-oriented caching. [Execution](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/execution.py) handles expansion, caching, errors/progress/interruption. [Server](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/server.py) validates queue submissions and supports prompt-specific interruption; missing prompt ID uses a global fallback. [Model management](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/comfy/model_management.py) provides load/offload/interruption. Core cache variants include classic/LRU/none/RAM-pressure.

**P:** native expansion, explicit order links, disk-valued completed results; cancellable media subprocesses; owned prompt cancellation; partial-result ledger. No manual hidden sampler loop or recursive POST to our own queue. Queue/progress events are not durable result success.

**U:** serial expanded execution alone does not bound memory: cached tensors can retain completed windows. M1 must demonstrate extension-scoped lifetime/release without global purges/settings changes. If not achievable, keep a bounded single-window path and revise batch execution before claiming long-input support. Worktrees do not isolate GPU/ports/output/models.

## Named extension candidates

All five repositories were publicly reachable at their pins. None was installed/imported. README behavior remains author-described where selected code did not corroborate it.

| Candidate | Actual inspected behavior | Use / boundary |
|---|---|---|
| AIMixer (S11) | README/node bind source v2v to `<Video 1>`; segment_runtime has skipped-source passthrough | UI/planning inspiration; these appearance-reference and missing-result semantics do not match mandatory structural-only VID2VA |
| Songssx (S12) | Finite code expands sampler/decode/finalize nodes, carries latent/audio/accumulated images; permitted lengths can exceed our cap; locked audio helper avoids repeated compressed seeking | Expansion/continuation reference, not proof of bounded RAM, strict <=15 s including context, Canny path or target GPU fit |
| DaSiWa (S13) | Director selects native mode models/lazy inputs; PyAV helper assigns rational PTS; README has optional prompt rewriting/continuity | Explicit mode state/reference UI/media inspiration; optional LLM integration is now an M2 product priority through a separate adapter, not wholesale runtime reuse |
| VHS (S14) | force_rate documented drop/duplicate; inspected CV path derives time from CAP_PROP_FPS/frame count | Convenience candidate, not evidence of VFR/offset correctness. Other decoder paths not audited |
| ReShot (S15) | IMAGE maps separate from VIDEO presets; resampler uses `i/src_fps` and only downsamples; fit can center-crop. README describes video-depth alignment/clip-wide normalization and first-run weight download | Optional Depth/Pose candidate; VIDEO path does not prove arbitrary VFR/upconversion. Depth internals not audited; use explicit IMAGE transform if later validated |

## Licenses

Core/Songssx/DaSiWa/VHS report GPL-3.0; AIMixer/ReShot/VideoX-Fun Apache-2.0; templates MIT. Models use a separate Community License. The inspected model LICENSE excludes the EU, UK, Republic of Korea and USA from the applicable territory and sets use/distribution obligations. This is a source fact, not a determination of deployment eligibility. Comfy conversions link the original license and name additional origins.

**P:** no third-party code/weights copied in M0. Foundation owner records file-level borrowing/attribution and a human-reviewed project license decision before M1 distribution. The GPU resource owner confirms environment/license applicability before execution. Local MVP excludes paid/API Context-IR and hosted 2K system components; S06 distinguishes those from released base weights.

## Unknowns and retrieval limitations

- Actual installed ComfyUI/Python/PyTorch/CUDA/kernel/model revisions and metadata are not supplied. M1 preflight needs separately authorized access, not an M0 scan/change.
- Target 16 GB/32 GB fit/time and actual Canny benefit need a real matched-profile sample. CPU/media/mocks cannot satisfy that gate.
- Short padding, seams, generated audio count, codec delay and release of cached tensors need measured receipts.
- Additional controls and complete creation-mode support have explicit M3 outcomes. Prompt automation, optional image identity and within-shot continuation now have M2 product gates; none is implemented. Mixed controls remain unknown and disabled.
- Neither named personal test asset was supplied. Do not scan for it, commit it or send it elsewhere. Canny can retain visual identity clues even with correct structural-only wiring.

The web GitHub edit link for JavaScript docs returned `Internal Error`; the expansion edit link requested GitHub sign-in. Pinned raw MDX succeeded via public read access, so these are parser/edit-route limitations, not unavailable projects. No selected primary-file access blocker remains. FFmpeg publication revision is unavailable and recorded as such.

## Revision source ledger and changes

Current public HEAD/model metadata was checked for S01–S15. All those pins match first M0 except S05: prior docs `1a33102d8b046b26644981ee2f4f8a1b99223fbc` → `9e719d0894db9f90a9056e602a09cfe6a2af3a32`. The four inspected English MDX pages were byte-identical at both pins. No new constraint follows from that update. S01–S04/S06–S10 native/model files and selected code/licenses for the old extension candidates were read again. S11/S12/S14/S15 README findings are retained from first M0 at unchanged pins; these are still scoped findings, not whole-repository audits.

| ID | New source / full HEAD revision | Upstream date UTC | Selected inspected files / license |
|---|---|---|---|
| S17 | [Prompt Enhancer](https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer/tree/66858ebd55a52924d4b113fcd518726b2038a77c), `66858ebd55a52924d4b113fcd518726b2038a77c` | 2026-08-29 17:25:30 | `prompt_enhancer_node.py`, `prompt_enhancer.py`, `prompt_guides.py`, `media_manifest.py`, `reference_resolution.py`, `gguf_server.py`, `api_routes.py`, `__init__.py`, `pyproject.toml`; prompt/contracts, media/manifest and architecture/GGUF guides plus media/shot v2 schema JSON; GPL-3.0-only |
| S18 | [Motion-Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context/tree/5335715abe54c1a9bfbe3494da29aae3e8635ce3), `5335715abe54c1a9bfbe3494da29aae3e8635ce3` | 2026-09-06 18:37:48 | `nodes.py`, `layout_contract.py`, `web/h3_motion_context.js`, README/CHANGELOG/pyproject/LICENSE; version 0.6.2, GPL-3.0 |
| S19 | [Qwen3-VL-4B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct/blob/ebb281ec70b05090aa6165b016eac8ec08e71b17/README.md), `ebb281ec70b05090aa6165b016eac8ec08e71b17` | 2025-10-15 16:15:55 | Model card + public metadata; declares Apache-2.0; root LICENSE retrieval 404 |
| S20 | [Qwen2.5-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct/blob/cc594898137f460bfe9f0759e9844b3ce807cfb5/README.md), `cc594898137f460bfe9f0759e9844b3ce807cfb5` | 2025-04-06 16:23:01 | Model card + public metadata; declares Apache-2.0; root LICENSE retrieval 404 |
| S21 | [Qwen3-VL source](https://github.com/QwenLM/Qwen3-VL/tree/96588727e44c78b25ba03ea03b8e12f7e64fd0da), `96588727e44c78b25ba03ea03b8e12f7e64fd0da` | 2026-01-30 04:47:30 | README, `qwen-vl-utils/src/qwen_vl_utils/vision_process.py`, LICENSE Apache-2.0 |
| S22 | [ComfyUI frontend](https://github.com/Comfy-Org/ComfyUI_frontend/tree/20b8abe962d73276d4603efac247ca928ae7110b), `20b8abe962d73276d4603efac247ca928ae7110b` | 2026-10-04 21:31:32 | `package.json`, `src/scripts/{app,api}.ts`, LICENSE GPL-3.0; HEAD package 1.56.2; S03 core requires frontend 1.53.10, not a tested pair |
| S23 | [FFmpeg scdet source](https://ffmpeg.org/doxygen/trunk/vf__scdet_8c_source.html), [filter docs](https://www.ffmpeg.org/ffmpeg-filters.html), [PySceneDetect detectors](https://www.scenedetect.com/docs/latest/api/detectors.html), [vLLM multimodal inputs](https://docs.vllm.ai/en/latest/features/multimodal_inputs/) | Unversioned publications, retrieved this audit | Scene-score metadata, detector interfaces and multimodal chat inputs. Actual future package/server/binary versions and licenses must be pinned before adoption |
| S24 | [Higgsfield](https://higgsfield.ai/) | Unversioned page, retrieved this audit | Outcome/workflow inspiration only, no API/equivalent backend claim |

Root LICENSE retrieval for S09 also returned 404; its card links S06's license and conversion origins. S08's card links LICENSE.md; the available LICENSE was inspected. These are file-route observations, not claims that the models lack license terms. Detailed session/model/machine provenance is private AO evidence and is intentionally absent from public documentation.

## Conditioning combinations

[Native ControlNet](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/comfy/ldm/minimax/controlnet.py) constructs zero control rows for reference/keyframe conditioning and applies map rows to `img_update` target-video positions. [Ref2VA](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/comfy_extras/nodes_minimax_h3.py) creates `minimax_refs` with text-encoder inputs and, when VAEs are connected, reference latent blocks. **I:** native structural and appearance paths can coexist. **U:** actual profile/weight loading, combined quality/memory and continuation alignment. M2-04/05 must validate the combinations, not combine separate demos into a PASS claim.

Native input is ordinary IMAGE, sliced to RGB and moved from NHWC to NCHW before VAE encoding. Prepare exact float `[N,H,W,3]` in 0..1; the video latent has 24 channels and the control branch expects 49 with mask/source additions or zero padding. Gray must be a declared three-channel luminance representation; ordinary CONTROL_NET or single-channel tensors are not interchangeable sockets. Reference image geometry has its own resize/token budget; target-video grid remains 32.

Card reference quotas are <=9 images, <=3 video clips, <=3 audios and <=12 physical files, with video/audio duration envelopes. Not every native direct call enforces every card quota; our future validator must. Paired `ref_video_audio_N` belongs to `ref_video_N`. Project subject/asset IDs persist, but `<Picture N>/<Video N>/<Audio N>` are derived from actual per-window physical bindings. The raw source motion video is not automatically registered as `<Video 1>` or an inpaint source.

## Prompt enhancer

The inspected [node definitions](https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer/blob/66858ebd55a52924d4b113fcd518726b2038a77c/prompt_enhancer_node.py) and `__init__.py` expose eight upstream nodes: `MiniMaxH3PromptGuideBuilder`, `MiniMaxH3PromptEnhancer`, `MiniMaxH3GGUFPromptEnhancer`, `MiniMaxH3PromptValidator`, `MiniMaxH3UnloadGGUFServer`, `MiniMaxH3MediaManifestValidator`, `MiniMaxH3ChainedMultishotOutput`, `MiniMaxH3ShotSelector`. None is our implemented node.

| Actual interface | Source-supported behavior / reuse boundary |
|---|---|
| Guide Builder | Basic prompt, mode, duration, reference_context and optional manifest/planning/audio/style fields → system/user strings, resolved mode/warnings, width/height. Model-free guide adapter candidate. |
| Enhancer / GGUF variant | Text/mode/time/metadata and endpoint/model/key or GGUF/server parameters → enhanced_prompt, validation_report, enhancement_manifest, effective duration/aspect, warnings, width/height. |
| Prompt / manifest validators | Strings → normalized data, validity/report/context. Syntax/binding checks do not prove rendered identity or model understanding. |
| Chained output / ShotSelector | Validate/select multishot prompt JSON. No automatic video/scene analysis; not our legal-window planner. |
| UnloadGGUFServer | Stops only enhancer-owned cached process, not unrelated services/models on a shared GPU. |

[Request code](https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer/blob/66858ebd55a52924d4b113fcd518726b2038a77c/prompt_enhancer.py) builds system/user **string** messages. Inspected sockets contain text/options/numbers, not IMAGE/VIDEO/AUDIO analysis input. Manifests describe media rather than carry video tensors. **F:** it is a text enhancer even with a local GGUF; an instruct GGUF does not thereby consume video. **P:** a separate VLM supplies reviewed observations and metadata first. H3's embedded Qwen provides conditioning hidden states, not this analysis stage.

The [mode guide](https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer/blob/66858ebd55a52924d4b113fcd518726b2038a77c/docs/prompt_contracts.md) specifies three ordered blocks for T2VA/I2VA/FL2VA/L2VA: `integrated_multimodal_description`, `overall_soundscape`, `non_diegetic_music`. Ref2VA has six: `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music`. Dialogue uses `<d>[Language] ...</d>` and local speaker markers. Reference tags must resolve. Preserve supplied dialogue/visible text; silent visual samples cannot establish a transcript. No-ref V2V can use a three-block base recipe while the native Ref2VA checkpoint has empty refs; this exact prompt/model combination still needs M1 runtime evidence.

[Manifest source](https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer/blob/66858ebd55a52924d4b113fcd518726b2038a77c/media_manifest.py) supports legacy items and `schemaVersion:2` logical assets/subjects/appearance states/environments/generations, active closure and inputMap/bindings. Registering metadata does not upload/connect files. Our adapter derives tags from actual sockets, not a second authoritative project registry. Its audio-only rejection is stricter than native S01, which accepts standalone audio without a visual input; do not treat that validator rule as a universal H3 restriction. Image-only binding is the first integration scope.

[Packaging](https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer/blob/66858ebd55a52924d4b113fcd518726b2038a77c/pyproject.toml) is version 0.14.1, Python >=3.10, no declared pip dependencies. It still needs ComfyUI context and a supplied service/model or llama-server binary for LLM use. API code supports OpenAI-compatible text chat and an LM Studio native route; remote endpoints require opt-in. No paid service is necessary. API compatibility does not establish vision inputs for every provider/model.

[GGUF source](https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer/blob/66858ebd55a52924d4b113fcd518726b2038a77c/gguf_server.py) launches an isolated process, defaults to nonpersistent use, and terminates/waits/kills in cleanup; Windows kill-on-close support exists. **F** mechanism, **U** measured peak/release/cancel behavior. The guide's complete-reclaim claim is not our receipt. Persistent mode needs explicit teardown completion before H3. This cleanup cannot unload an unrelated LM Studio/Ollama/API server.

Adapter conflicts: enhancer allows experimental durations up to 150 s and frame counts beyond our cap; its dimension output is 16-aligned, while native target requires 32. The window planner/spatial transform must remain authoritative. Reject mismatches; do not silently wire duration/size outputs over source-preserving settings. Pin guide/manifest/adapter versions separately; preserve accepted user edits on reanalysis. Manual canonical blocks and model-free builder/validator remain available if optional enhancer/VLM is absent. They do not satisfy the automatic-VLM acceptance gate.

## Scene detection and Qwen analysis

**F S23:** FFmpeg scdet emits per-frame change-score metadata. PySceneDetect ContentDetector compares adjacent content; AdaptiveDetector uses a rolling change baseline to reduce fast-camera false positives. Neither proves narrative scene boundaries. **P:** first candidate is streamed FFmpeg detection over canonical media with thresholds/minimum intervals and full frame-index mapping. Optional PySceneDetect requires an actual package/license pin before adoption. Display scored proposals, then accept/move/delete manually. Flashes, HUD overlays, pans, fades and dissolves require correction. Technical H3 window edges never become scenes automatically.

| VLM option | Actual supported interface | Unknown / decision |
|---|---|---|
| Qwen3-VL-4B-Instruct | **F S19/S21:** Qwen3VLForConditionalGeneration + AutoProcessor multimodal chat; frame lists/video tensors/metadata, fps/num_frames and visual budgets | Proposed first local Transformers candidate; not H3's 32B encoder. Windows dependency pair/quantization/fit unverified. |
| Qwen2.5-VL-7B-Instruct | **F S20:** Qwen2_5_VLForConditionalGeneration + AutoProcessor + qwen_vl_utils.process_vision_info; video/multiple images and pixel bounds | Supported fallback interface; larger model, no target quality/fit comparison. |
| Existing configured multimodal endpoint | **F S23:** vLLM chat accepts image_url parts/multiple images; video payloads are backend-specific | Timestamped bounded images candidate. Validate exact served Qwen/backend version. No mandatory vLLM/WSL, source-video upload or assumed vision on a text route. |

**P sampling:** scene chunks <=12 s; endpoints plus evenly spaced samples near 1 FPS, <=16 frames/request and <=512x512 equivalent area/frame. Stream/decode/discard canonical frames, saving sample times/IDs/hashes and max gaps. S21's video frame factor is 2; any duplicate for even batching is labeled, with no extra time coverage. Use real frame-index/timestamp metadata; irregular samples need validated metadata or timestamped images, not a fictional constant fps. Every temporal chunk gets coverage, but sparse sampling can miss fast events; show uncertainty and allow resampling. Bounded text reduction persists summaries without an ever-growing all-scene prompt/history.

Drafts separate source game/low-poly appearance from desired photorealistic style, observed camera/action from guesses, and user-selected subject bindings from generated labels. No invented transcript from images. Analysis and guide format versions are separate in [CONTRACTS](CONTRACTS.md#sceneanalysis-and-detectionproposal).

Model phases: CPU normalization/detection/sampling → bounded VLM → persist analysis and stop owned analyzer → text enhancement → persist drafts and stop owned enhancer → H3 render. Freeze a run's snapshot; new edits explicitly cancel/replan or affect the next run. H3 offload uses native model management. No global purge or killing unrelated processes. Measure process exit, residency, attention/KV memory and H3 load peaks before claiming fit on the target 16 GB/32 GB machine.

## Motion-Context

[nodes.py](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context/blob/5335715abe54c1a9bfbe3494da29aae3e8635ce3/nodes.py) takes current CONDITIONING/VAE/LATENT plus prior context_latent or frames, optionally audio VAE/audio; returns CONDITIONING and trim_frames. Video contexts offered: 5/22/39/56. Direct tail slicing requires compatible dimensions/channels and latent-step phase. Default head anchoring uses timeline-aligned audio, independently sized (default 24 frames; 0 follows video). It adds minimax_keyframes, preserves other metadata/refs and later anchors, and drops conflicting head anchors. These are source mechanisms, not perfect-motion results.

[layout_contract.py](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context/blob/5335715abe54c1a9bfbe3494da29aae3e8635ce3/layout_contract.py) tests private PackedLayout arithmetic, ref cursor shifts, fractional/negative audio anchors and timing before use. README requires core 0.34.0+; older 0.3.1 patched layout, current 0.6.2 does not replace that constructor. Native Fun tutorial requires 0.35.0+; version labels alone are insufficient. S01 retains relevant position arithmetic: **I** source plausibility, **U** actual combined execution.

Trim removes the head from both streams and optionally trims/zero-pads audio to remaining duration. Its local rounded sample slices are not our global absolute Q accounting, especially at 32 kHz. Use actual trim_frames as evidence, with our finalizer owning exactly-once trim; never run both trims on the same overlap.

Save/Load stores video/audio safetensors in indexed slots. Load 0 has no predecessor; loaded samples are a special list for context input, not stock decodable LATENT. Slot names/mtime are not content-hashed compatible project checkpoints. The frontend calls app.queuePrompt, advances grouped widgets on events and can loop with no explicit count stop. Reuse neither this unlimited chain nor slot-clearing routes wholesale. Optional torchaudio resampling and safetensors still depend on available environment.

**P M2-05 experiment:** matched native ControlNet + image refs + context profile; same resolution/VAEs; initially 22 head-context frames, total N<=345. Explicitly set `audio_context_length=0` to follow the picture span; do not inherit the independently longer default 24. Actual 40 Hz grid overhang/timing still needs mapping and budget checks; earlier independent audio history remains disabled until a tested complete-extent profile exists. Control maps must cover the same inference timeline: prior head cannot accidentally receive next useful-source frames. Record predecessor maps or a separately tested neutral-head policy. Preserve source audio still comes from assembly PCM. Generated-audio continuation has separate alignment/sample/seam checks. Reset at real cuts, explicit reset and incompatible profile/geometry; retain subject bindings for identity across cuts. Predecessor edits invalidate successors within the continuity group. No such state is an M1 dependency.

**F/I tail hazard:** direct latent context slices the end of the prior native output, not our last useful endpoint. If that output contains tail padding, its last 22 frames can include held frames. Do not assume it is a valid motion tail. Require a verified useful-end/latent-phase map; replan nonterminal continuation windows without tail pad or use a tested bounded decoded-useful-tail re-encode. This tradeoff is explicit in [window/state contracts](CONTRACTS.md#generationwindow-and-capabilities).

## UI feasibility

Inspected the [main Director screenshot](https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes/blob/afd009473efa1ccff88fa41c557dce94ad9195c3/assets/DaSiWa-MiniMaxH3-Director.png): dark compact panels, mode pills, source/canvas size readouts, separate reference tiles, expandable continuity, Load/Save and visible structured prompts. [Frontend code](https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes/blob/afd009473efa1ccff88fa41c557dce94ad9195c3/js/minimax_h3_director.js) uses app.registerExtension, addDOMWidget, preview/dialog overlays and serialize/configure hooks. Transfer those ideas to a project overview/selected-scene panel with clear inheritance, errors, numeric markers and persistent state. Our timeline/ruler/window overlay still needs independent implementation; this image is not proof of it.

S05 documents WEB_DIRECTORY/JS hooks; S22 confirms extension/queue/event APIs in current frontend source. S22 HEAD 1.56.2 differs from core's declared 1.53.10. Choose/test an actual pair and required hooks; do not claim universal frontend compatibility. Avoid copying global/private widget hijacks and broad runtime. DaSiWa's own ref/inpaint/LLM rules do not become product requirements through visual inspiration.

## Reuse, resources and licensing additions

| Area | Recommended reuse / separate work |
|---|---|
| Native H3 | Reuse graph execution/Canny/VAEs/sampler/model management through pinned schemas. Build disk media/window/result adapters separately. |
| Prompts | Optional enhancer guide/text/manifest adapter; build bounded VLM scene analysis and draft review separately. Project state remains authoritative. |
| Continuation | Evaluate a bounded state adapter using Motion-Context math; retain own hashed receipts, quotas, request reconciliation and cut policy. |
| UI | DaSiWa visual grouping/dialog/card ideas; independent timeline/editor/runner. |
| Controls | Native Canny first; optional validated preprocessors later. No map blend establishes mixed support. |

Baseline remains native expansion **per bounded window**. One full expanded project graph may retain every intermediate; serial ordering alone does not prove release. Require a measured RAM/VRAM plateau across prompts without silently changing global cache settings. Failure blocks long-run acceptance, not the measured short path. Disk quotas cover canonical/proxy/map/result/state artifacts; streaming does not provide unlimited disk/time. Atomic receipts/checkpoints plus queue/history reconciliation support resume. Worktrees do not isolate GPU/venv/ports/output/model settings; one allocated sequential owner controls shared runtime work.

S17 is GPL-3.0-only, S18/S22 GPL-3.0, Qwen source Apache-2.0 and model cards declare Apache-2.0. Root LICENSE 404s require checking actual future distributions/notices. No project license is chosen or third-party source copied here. Copying GPL code requires compatible distribution/notices; visual inspiration and protocol adapters are distinct reuse choices. H3/Fun weight terms remain separate, including territorial and output-use restrictions; future runtime owner confirms applicability. Hosted Context-IR/2K components are not all released; our local analyzer/enhancer is a proposal, not equivalent hosted functionality.

Unverified: target installed component versions, all model fits/timings, actual no-ref prompt recipe, combined ref/control/context quality, audio seams, short padding, long-run cache lifetime and VLM/detector accuracy. M0 document checks and upstream examples establish no runtime PASS. See [PLAN document verification](PLAN.md#document-verification).
