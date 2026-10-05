# M1 local Project storage

The human narrowed the foundation storage scope on 2026-10-05 to ordinary local,
single-user ComfyUI Project load/save. This explicitly supersedes the earlier
directory-isolation implementation and adversarial filesystem acceptance scope.
Accepted documentation base remains C0
`7960568eff779c8c35c3d28a985a243368b91c26`; the previously published implementation
is `fdce306ce6b7ac4c38491b593b6a821555d224c3`. The preserved brief is unchanged.

## Supported operating contract

Select an existing local project folder. Project/media inputs are ordinary
regular files, and folder names, links and filesystem objects remain stable
during an operation. Serialized locators remain normalized project-relative
paths. Basic traversal/absolute-path checks and resolved-path containment reject
invalid locations; they are not an OS security boundary against another local
process deliberately changing filesystem objects during I/O. Changing junction
layouts and special-device inputs are outside the supported contract.

Standard Python file operations stage a complete UTF-8 Project beside its
destination and publish it atomically where the filesystem supports the
required replace/link operation. Explicit overwrite, Project ID/revision checks
and the existing publication lease coordinate writers using this API. Other
editors do not participate in that protocol. Ordinary failures before
publication preserve the previous file and remove the staged partial.
Publication is the commit point; later cleanup errors produce a redacted warning
and return the committed save rather than falsely reporting failed replacement.

Readers check regular-file type before opening. Missing, unreadable, malformed
and cyclic paths produce the existing structured, path-redacted errors.
Migration writes a separate file and preserves its source. Explicit listed
asset checks hash regular files only; no search, relink guess or decoding occurs.

## Review history and changed assumptions

The [exact fdce review](https://github.com/KillMeINoobs/MiniMaxH3-MovieMaker/pull/2#pullrequestreview-5409824233)
found F2-F9 resolved, F1b still open under the previously advertised isolation
contract, F10 path-resolution errors, and a source-derived POSIX FIFO concern
F11. The junction case is historical evidence of that implementation's failed
isolation claim; it is not labelled fixed. The special directory-handle layer
and its two adversarial rename/swap tests are retired under the explicit new
operating assumptions. No adversarial probes are rerun for this outcome.

Useful F10 typed/redacted resolution handling is retained. The simpler regular
input check addresses the F11 source concern under stable-folder assumptions;
actual POSIX FIFO/runtime verification remains NOT PERFORMED in this Windows
session. F2-F9 record, import and revision improvements remain required.
The new exact candidate requires independent review against this revised
contract. Prior review does not approve it. Schema and worker interfaces remain
`2.0.0`; the four Project nodes and nine downstream callable signatures remain
unchanged.

## Implementation and verification sequence

1. Inventory and preserve the useful local F10 changes. Replace native directory
   isolation in `contracts/confined_io.py` and `project_io.py` with ordinary
   Python path/file operations, retaining the existing save revision/lease guard.
2. Keep relevant contracts/import/conformance tests. Add normal-use and ordinary
   failure regressions in the existing I/O tests: Unicode/spaces, regular inputs,
   explicit overwrite, original preservation, missing/malformed/cyclic paths
   and staged/publication failure cleanup. Mark POSIX-only checks honestly.
3. Reconcile the handoff, validation receipt, README and journal; verify schemas,
   presentation, brief/ledger/privacy and base-to-candidate diff. Publish the
   checked feature follow-up to draft PR #2 and report its exact SHA through AO.

At this scope decision, deployment/restart and runtime execution were still
unperformed. The reviewed `20541f9` snapshot was subsequently deployed and
human-restarted; four-class registration passed. Its UI fixture needs a scoped
readiness/checker correction. The subsequent reviewed ac335 archive retained
the same backend and registration; ordinary selector interaction/readback has
partial browser evidence. Complete native graph/layout checks remain blocked,
as recorded in [validation](../validation/M1_FOUNDATION.md). The new checker
follow-up changes no storage assumptions or backend code. Shared ownership is retained;
CF remains unaccepted. Node/workflow execution, queues, inference, weights,
user-video decoding/output inspection and GPU work remain unperformed.
