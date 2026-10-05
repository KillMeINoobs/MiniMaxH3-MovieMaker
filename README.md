# ComfyUI-KMIN-VideoDirector

The M1 foundation implements portable Projects and four ComfyUI Project nodes.
The intended first product mode is video-to-video: gameplay or low-poly video
to cinematic output with structural control and editable scene prompts.
Media processing and H3 generation belong to the next outcomes and are not
implemented here. Photorealism, GPU fit and video quality remain unverified.

This is a **draft foundation**. Synthetic CPU and presentation checks are
recorded in [M1 foundation validation](docs/validation/M1_FOUNDATION.md).
The human restarted reviewed205; the later source/CPU-reviewed `ac335b8`
snapshot retains its identical backend and all four registered Project classes.
The ordinary selector saved Russian and restored English with verified server
readback. Complete browser layout/native graph save/reload remain **BLOCKED**.
A new checker compatibility/diagnostic correction needs pinned review and a
fresh live check. **GPU NOT PERFORMED.**
No workflow was queued, model loaded, inference performed or user video decoded.

## Available nodes

| Stable class ID | Purpose |
|---|---|
| `KVD_ProjectJSON` | Validate Project JSON; return a Project, canonical JSON and structural report. |
| `KVD_LoadProject` | Load a relative Project file from an explicitly selected local folder. |
| `KVD_SaveProject` | Save a Project atomically; overwrite is explicit and revision checked. |
| `KVD_ValidateProject` | Revalidate the Project and report structural evidence. |

These nodes use `KVD_PROJECT` connections. Validation does not decode, generate
or prove asset availability. Reports distinguish structure, unchecked assets
and unperformed GPU work. Missing files and invalid records return shared error
codes. Project JSON starts empty; provide a Project or load the synthetic example.

The interface defaults to English. Use the visible **EN / RU** selector in a
KVD node panel, or **Settings → KVD → Interface → Language / Язык (EN / RU)**.
The persisted setting is `KVD.Language`. Changing language translates our
labels, help, errors and status; stable keys, values, enum semantics and
connections remain unchanged. Native ComfyUI and other packs keep their own
presentation. Selector text/save readback has partial actual browser evidence;
complete layout and graph roundtrip acceptance is still blocked.

## Portable data and extension interfaces

[KVD-WORKER/2.0.0](docs/FOUNDATION_HANDOFF.md) documents actual imports,
record types, callable signatures, extension registration and ownership.
Bundled [schemas](schemas/project.schema.json) describe the data structure;
the stdlib Python validator also checks interval coverage, ID/hash closure,
selected streams, settings inheritance and other relations.

Projects use integer 24 FPS intervals `[start,end)`, stable identifiers,
project-relative Unicode paths and content hashes. Seeds are decimal strings
including the unsigned 64-bit range. JSON round-trips canonically; unknown
schema majors/required features and invalid locators/ranges/digests are rejected.
The explicit v1-example migration writes a separate file and preserves its
source. It is a narrow conformance migration, not support for every old format.

Depth/Pose/VLM/enhancer/model packages are absent from foundation imports.
Future analysis/reference/continuation data can be stored and checked;
unsupported operations are rejected. The nine downstream protocols have no
registered execution handlers. Owned modules can add real nodes/handlers and
translations without changing shared package files.

## Setup and checks

Runtime dependencies are the Python standard library (Python 3.10+). No pip
install, model download or core/other-pack update is needed for this foundation.
For registration, copy an explicitly selected repository snapshot into a new
`custom_nodes/ComfyUI-KMIN-VideoDirector` directory in the **actual running
installation**. Keep `__init__.py`, `kmin_video_director/`, `schemas/` and `web/`
together. Avoid duplicate copies; use the running application's supported
restart after saving work and confirming the queue is idle. A CLI's default
workspace may differ from the running Desktop installation.

[workflows/foundation_project.json](workflows/foundation_project.json) is a
synthetic UI fixture for four actual Project nodes and two connections.
It contains missing synthetic assets and planned metadata, with no generation
nodes. It is not the downstream V2V workflow. Current live verification is
**load/serialize/inspect only; do not queue it**.

CPU checks use an isolated verification environment; do not install verification
dependencies in the shared ComfyUI venv. Checked development dependency versions
are in [requirements-verify.lock](requirements-verify.lock).

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-verify.lock
.venv/Scripts/python -m pytest tests/contracts tests/imports -q
node --experimental-vm-modules --test tests/ui/presentation.test.mjs tests/ui/language.test.mjs tests/ui/verification.test.mjs
git diff <accepted-base> HEAD --check
```

Unix uses `.venv/bin/python`. The CPU suite validates synthetic records with an
independent Draft 2020-12 validator, exercises Project-only I/O in temporary
folders, blocks optional imports and checks every downstream call shape. It
performs no media decoding, model inference or ComfyUI queue submission. Node's
VM-module flag is used only to test the actual frontend module against a
synthetic native host; those tests are not browser acceptance.

Project load/save supports an existing user-selected local folder, regular files
and a stable folder layout during operations. Standard Python operations check
relative paths and regular inputs, stage complete JSON and publish atomically
where replace/link is supported. Explicit overwrite and the existing cooperative
publication/revision guard protect normal API saves from stale revisions. Missing,
malformed and cyclic paths give typed errors. This is ordinary local storage;
it provides no OS security boundary against another process deliberately changing
filesystem objects during I/O. See the [storage scope](docs/decisions/M1_LOCAL_STORAGE_SCOPE.md)
and [validation receipt](docs/validation/M1_FOUNDATION.md) for the changed operating
assumptions and historical review. POSIX runtime checks remain NOT PERFORMED.

## Project documents

Read the [preserved brief](docs/PROJECT_BRIEF.md),
[superseding V2V direction](docs/PRODUCT_DIRECTION_V2V.md),
[pinned research](docs/RESEARCH.md), [architecture](docs/ARCHITECTURE.md),
[contracts](docs/CONTRACTS.md), [node inventory](docs/NODE_CATALOG.md),
[workflow specification](docs/WORKFLOW_SPEC.md), [plan](docs/PLAN.md) and
[task journal](docs/tasks/INDEX.md). The
[M1 execution decision](docs/decisions/M1_EXECUTION_SCOPE.md) records later
human authorization and the manual-generation boundary separately from the
brief. Accepted C0 is `7960568eff779c8c35c3d28a985a243368b91c26`; it includes the
merged M0 final head. A separately reviewed, checked CF is still pending.

M1-04 prepares a real workflow for the **human** to run. Workers do not perform
H3/VLM/enhancer generation, download weights or inspect generated user-video
output. M2/M3 remain gated. A locally supplied sample stays outside public
artifacts and has not been decoded by foundation.

The brief is preserved byte for byte; the research ledger remains pinned.
No personal media, model weights or third-party implementation is bundled.
DaSiWa is visual inspiration only. Project license selection remains open;
see [notices](NOTICES.md) and the [component license ledger](docs/RESEARCH.md#licenses).
