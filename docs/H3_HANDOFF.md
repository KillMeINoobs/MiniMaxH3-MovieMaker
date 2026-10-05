# M1 Canny and native H3 implementation plan

Source dependency: `ac335b87c966b3353c5115c663d4344ff08c01a0`, descended
from accepted C0 `7960568eff779c8c35c3d28a985a243368b91c26`. Independent
review 5413276074 approved source/CPU evidence only. Full foundation live
acceptance remains blocked. The implementation assignment separately releases
owned CPU work; it does not release shared runtime or generation.

## Scope and design

Implement the four unchanged KVD-WORKER/2.0.0 operations: BuildControl,
CompileWindowPrompt, ExpandNativeRender and FinalizeWindow. Import immutable
records and runtime envelopes from foundation. Register actual implementations
and nodes through owned `nodes/h3/*_nodes.py`; use shared presentation and
verified KVD.Language helpers. Optional runtime packages remain lazy.

The first recipe uses Canny or explicit structural off, authored visible text,
empty reference/guide/inpaint inputs and no continuation. A bounded window has
24 FPS, a profile-derived upward `5+17*k` length between 124 and 345 including
all padding, exact canvas geometry and exact useful finalization. Native
conditioning, sampling, decoding, interruption and model management remain
native graph operations. Missing schemas/models/backends fail explicitly.

## Implementation steps

1. Inspect narrowly pinned primary native H3, Canny, graph-expansion, sampler
   and model metadata. Record public source/license provenance. Write failing
   owned tests for thresholds, contour geometry, authored text/digests, profile
   rejection and no-reference policy; implement those pure CPU portions.
2. Add deterministic native graph creation and required class/port/link/schema
   checks. Verify observable graph settings, off behavior, serial ordering and
   cancellation against pinned source and the separately supplied read-only
   installed-schema handoff. Implement checked durable useful finalization;
   label synthetic decoded outputs and CPU evidence honestly.
3. Add import-safe discoverable nodes and scoped EN/RU presentation. Test
   actual registrations, signatures, unchanged semantic data/custom titles,
   status/help and failures. Document callable fields and manual setup.
4. Integrate actual media helpers only after an explicitly supplied reviewed
   common SHA containing media. Produce `workflows/m1_short_v2v.json` from real
   interfaces, labelled diagnostic until installed preflight and human results.
5. Run the owned CPU/schema/import/frontend checks in an isolated environment
   with unchanged verification lock. Report obsolete shared assertions at the
   initial dependency separately. Verify brief/ledger and owned diff, freeze
   checked local commits, and await the coordinator's exact PR base/ref before
   publishing the one authorized draft candidate for separate review.

No H3/GPU/video-generation result, installed node, usable native graph or GPU
fit is claimed by this plan. M2/M3 and long-run memory acceptance remain gated.
