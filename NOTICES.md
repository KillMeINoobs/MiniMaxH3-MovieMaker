# Code, component and license status

Project license selection remains **unselected**. This is an authorized draft
implementation for inspection, not a claim of an open-source license grant or
a released V2V product. The owner/reviewer must record the distribution license
decision before a release. No model weights or user media are distributed.

The new foundation code, schemas, fixtures and styling were written for this
project. No DaSiWa, Director, enhancer, Motion-Context, native ComfyUI code or
artwork was copied. DaSiWa's compact grouping and restrained palette are visual
inspiration only. References to APIs and graph contracts are interoperability
work, not bundled third-party implementations.

Runtime dependencies: Python standard library only. ComfyUI provides its own
frontend APIs when this directory is installed as a custom-node pack. The core
and frontend are external GPL-3.0 components; their code is not shipped here.
The [pinned source ledger](docs/RESEARCH.md#source-ledger) records inspected
upstream revisions/licenses and keeps model Community License terms separate.

Verification-only dependencies are isolated from ComfyUI and pinned in
`requirements-verify.lock`. Pytest 8.4.2 and jsonschema 4.26.0 declare MIT
licenses. Their installed dependencies are not vendored. The frontend
presentation test uses Node's built-in test runner; no npm installation is
required. This notice does not replace the external components' license terms.
