# M0 primary-source research

Inspected **2026-10-04 UTC / 2026-10-05 Europe/Moscow**. Only selected source/docs/JSON and repository/model metadata were fetched. No clone, weights, install, ComfyUI change, inference, user-asset access or upload. **GPU validation NOT PERFORMED.**

Evidence labels: **F** direct source fact; **I** inference; **P** project proposal; **U** unknown; **R** independently observed runtime result. There are no H3 R results in M0. Publisher examples/performance statements are not our receipts.

## Source ledger

These are inspected snapshots, not instructions to update the user's installation. Path lists delimit inspection scope. GitHub metadata and license openings were inspected; a license identifier does not decide this project's eventual license. Links use full revisions except the explicitly unversioned FFmpeg publications.

| ID | Source and full revision | Upstream commit/model date (UTC) | Selected paths inspected | License |
|---|---|---|---|---|
| S01 | [ComfyUI core](https://github.com/Comfy-Org/ComfyUI/tree/b87fe48b0491425f682f7ffdaed56d0387cb6c5d), `b87fe48b0491425f682f7ffdaed56d0387cb6c5d` | 2026-10-04 19:06:36 | `comfy_extras/nodes_minimax_h3.py`, `nodes_model_patch.py`; `comfy/ldm/minimax/controlnet.py`, `model.py`, `vae.py` | [LICENSE](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/LICENSE), GPL-3.0 |
| S02 | Same core revision/date | Same | `execution.py`, `server.py`, `comfy_execution/graph_utils.py`, `comfy/model_management.py`, `comfy/utils.py` | Same core license |
| S03 | Same core revision/date | Same | `comfy_extras/nodes_canny.py`, `nodes_video.py`; targeted H3 search in `comfy/controlnet.py` | Same core license |
| S04 | [Native template](https://github.com/Comfy-Org/workflow_templates/blob/0e5c5efb32ba6f3365d6da07da64aaf668157042/templates/video_minimax_h3_fun_controlnet_union.json), `0e5c5efb32ba6f3365d6da07da64aaf668157042` | 2026-10-02 19:28:52 | `templates/video_minimax_h3_fun_controlnet_union.json`, top-level nodes/links/widgets/model metadata and pose subgraph | [LICENSE](https://github.com/Comfy-Org/workflow_templates/blob/0e5c5efb32ba6f3365d6da07da64aaf668157042/LICENSE), MIT |
| S05 | [Comfy docs](https://github.com/Comfy-Org/docs/tree/1a33102d8b046b26644981ee2f4f8a1b99223fbc), `1a33102d8b046b26644981ee2f4f8a1b99223fbc` | 2026-10-04 05:02:17 | `custom-nodes/backend/expansion.mdx`, `custom-nodes/js/javascript_overview.mdx`, `tutorials/video/minimax/minimax-h3.mdx`, `minimax-h3-fun-controlnet.mdx` | [LICENSE](https://github.com/Comfy-Org/docs/blob/1a33102d8b046b26644981ee2f4f8a1b99223fbc/LICENSE), GPL-3.0 |
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

Node property strings such as 0.33.0 and older subgraph versions are serialization metadata, not a verified minimum runtime. [Pinned control tutorial](https://github.com/Comfy-Org/docs/blob/1a33102d8b046b26644981ee2f4f8a1b99223fbc/tutorials/video/minimax/minimax-h3-fun-controlnet.mdx) specifies **0.35.0+** and both base families. Preflight actual node schemas/loader instead of accepting a version alone.

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

**F:** [expansion docs](https://github.com/Comfy-Org/docs/blob/1a33102d8b046b26644981ee2f4f8a1b99223fbc/custom-nodes/backend/expansion.mdx) specify result links/subgraph, deterministic unique IDs and link-oriented caching. [Execution](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/execution.py) handles expansion, caching, errors/progress/interruption. [Server](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/server.py) validates queue submissions and supports prompt-specific interruption; missing prompt ID uses a global fallback. [Model management](https://github.com/Comfy-Org/ComfyUI/blob/b87fe48b0491425f682f7ffdaed56d0387cb6c5d/comfy/model_management.py) provides load/offload/interruption. Core cache variants include classic/LRU/none/RAM-pressure.

**P:** native expansion, explicit order links, disk-valued completed results; cancellable media subprocesses; owned prompt cancellation; partial-result ledger. No manual hidden sampler loop or recursive POST to our own queue. Queue/progress events are not durable result success.

**U:** serial expanded execution alone does not bound memory: cached tensors can retain completed windows. M1 must demonstrate extension-scoped lifetime/release without global purges/settings changes. If not achievable, keep a bounded single-window path and revise batch execution before claiming long-input support. Worktrees do not isolate GPU/ports/output/models.

## Named extension candidates

All five repositories were publicly reachable at their pins. None was installed/imported. README behavior remains author-described where selected code did not corroborate it.

| Candidate | Actual inspected behavior | Use / boundary |
|---|---|---|
| AIMixer (S11) | README/node bind source v2v to `<Video 1>`; segment_runtime has skipped-source passthrough | UI/planning inspiration; these appearance-reference and missing-result semantics do not match mandatory structural-only VID2VA |
| Songssx (S12) | Finite code expands sampler/decode/finalize nodes, carries latent/audio/accumulated images; permitted lengths can exceed our cap; locked audio helper avoids repeated compressed seeking | Expansion/continuation reference, not proof of bounded RAM, strict <=15 s including context, Canny path or target GPU fit |
| DaSiWa (S13) | Director selects native mode models/lazy inputs; PyAV helper assigns rational PTS; README has optional prompt rewriting/continuity | Explicit mode state/reference UI/media inspiration; broad optional surface and LLM rewriting are not dependencies |
| VHS (S14) | force_rate documented drop/duplicate; inspected CV path derives time from CAP_PROP_FPS/frame count | Convenience candidate, not evidence of VFR/offset correctness. Other decoder paths not audited |
| ReShot (S15) | IMAGE maps separate from VIDEO presets; resampler uses `i/src_fps` and only downsamples; fit can center-crop. README describes video-depth alignment/clip-wide normalization and first-run weight download | Optional Depth/Pose candidate; VIDEO path does not prove arbitrary VFR/upconversion. Depth internals not audited; use explicit IMAGE transform if later validated |

## Licenses

Core/Songssx/DaSiWa/VHS report GPL-3.0; AIMixer/ReShot/VideoX-Fun Apache-2.0; templates MIT. Models use a separate Community License. The inspected model LICENSE excludes the EU, UK, Republic of Korea and USA from the applicable territory and sets use/distribution obligations. This is a source fact, not a determination of deployment eligibility. Comfy conversions link the original license and name additional origins.

**P:** no third-party code/weights copied in M0. Foundation owner records file-level borrowing/attribution and a human-reviewed project license decision before M1 distribution. The GPU resource owner confirms environment/license applicability before execution. Local MVP excludes paid/API Context-IR and hosted 2K system components; S06 distinguishes those from released base weights.

## Unknowns and retrieval limitations

- Actual installed ComfyUI/Python/PyTorch/CUDA/kernel/model revisions and metadata are not supplied. M1 preflight needs separately authorized access, not an M0 scan/change.
- Target 16 GB/32 GB fit/time and actual Canny benefit need a real matched-profile sample. CPU/media/mocks cannot satisfy that gate.
- Short padding, seams, generated audio count, codec delay and release of cached tensors need measured receipts.
- Mixed controls and complete T2VA/I2VA/FL2VA/L2VA/REF2VA product support remain deferred. Source-supported modes do not imply our extension exists.
- Neither named personal test asset was supplied. Do not scan for it, commit it or send it elsewhere. Canny can retain visual identity clues even with correct structural-only wiring.

The web GitHub edit link for JavaScript docs returned `Internal Error`; the expansion edit link requested GitHub sign-in. Pinned raw MDX succeeded via public read access, so these are parser/edit-route limitations, not unavailable projects. No selected primary-file access blocker remains. FFmpeg publication revision is unavailable and recorded as such.

## Session provenance

Pre-edit HEAD, origin/main and live remote main matched `8e8cf7253862f94b7787d7065babf2878064ef82`. Source snapshots are listed above. Client evidence records Codex 0.160.0, model **gpt-6.1-sol**, actual turn reasoning **max**. AO effort/override fields were empty; actual native turn evidence takes precedence over catalog defaults. Detailed machine/session diagnostics remain in the private AO handoff.
