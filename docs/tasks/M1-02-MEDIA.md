# M1-02 — Canonical media, window planning and accurate export

- **Goal:** a source-independent proof of exact 24 FPS coverage, legal windows, preserved display geometry and nonaccumulating audio timeline.
- **Scope:** actual-PTS probe/normalization to disk; fingerprint/timing manifest; balanced frame planner; bounded window preparation, rotation/SAR/padding; continuous PCM/sample boundaries; ordered checked CPU export and layer-specific cache invalidation. Own ordinary logic/media tests and docs with this result.
- **Non-goals:** neural inference, ControlNet loading, UI editor, hidden RGB references, continuation, resuming queue requests.
- **Inputs/read paths:** shared M1-01 output on CF; `AGENTS.md`, `docs/PROJECT_BRIEF.md`, `docs/CONTRACTS.md` media/window/spatial/audio sections, `docs/RESEARCH.md` S01/S03/S16, `docs/ARCHITECTURE.md`, `docs/PLAN.md`, journal.
- **Outputs/owned areas (proposed):** `kmin_video_director/media/`, `planning/`, `assembly/`; corresponding ordinary tests/synthetic fixtures; media validation documentation. Shared schemas/package/dependencies stay with foundation owner.
- **Dependencies/base requirement:** start only from integrated reviewed checked **CF**, exact full SHA recorded, interfaces present there. Integrate result as CM and record checks/SHA. Adapter may work on CF but must integrate CM before consuming real media code; no unmerged-branch assumption.
- **Interface version:** `KVD-WORKER/1.0.0` ProbeMedia/NormalizeMedia/PlanWindows/PrepareWindow/AssembleExport; schema 1.0.0. Common changes go through foundation owner and a new base.
- **Acceptance evidence:** actual decoded CFR PTS 1/24 and exact F; short tail/360/long balanced coverage, all N lattice/cap valid; padding absent from output; 23.976/29.97/30/60/VFR and missing EOF timing handled; audio +/- offsets and boundary impulses with Q rounding, one encode and measured codec delay; mute/no audio; 4:3/portrait/rotation/SAR/off-grid/odd codec sizes; spaces/Cyrillic paths; prompt does not invalidate Canny preparation dependencies; streaming memory checked. No H3/GPU PASS claim.
- **Environment/resources:** approved synthetic media, authorized existing FFmpeg/ffprobe or chosen equivalent; record binary/version/build. CPU only, Windows paths, no personal-asset search, no dependency installation beyond assignment scope or user ComfyUI changes. Fixture generation is future task work, not performed in M0.
- **Publication policy:** future assignment must explicitly authorize publishing; ordinary tests/docs in same outcome PR. Personal media private; no weights. Separate reviewer; owner fixes failures.
- **Status/blockers:** PROPOSED / NOT STARTED; waits for CF, owner/environment authorization and implementation scope. User's two named test files are not available.

## Journal

M0: contracts and acceptance described only; no FFmpeg/media/unit tests executed.
