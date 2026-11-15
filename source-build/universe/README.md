# Universe recipe development

Universe is for extensions whose dependency burden makes Debian packaging
prohibitive. Ordinary extensions should use Debian packaging; Rust extensions
use PGRX. Document the specific obstacles and shipped-component evidence in
`PACKAGING.md`.

Start from the [Dockerfile, README and metadata templates](templates/).
They use the existing scaffolder and do not require a separate generator:

```sh
dagger call -sm ./dagger/maintenance/ create \
  --name=my-extension --versions=18 --distros=trixie \
  --templates-dir=./source-build/universe/templates \
  export --path=./universe/my-extension
```

Replace all TODOs and placeholders. Follow the [pg-duckdb recipe](../../universe/pg-duckdb/)
for a completed example. Keep the public README focused on installation and use;
put the Debian packaging rationale and a short SBOM overview in `PACKAGING.md`.

The Dockerfile owns source acquisition, compilation and payload staging. It copies
`source-build/` broadly into the builder, uses the shared SBOM generator's hook
interface, and copies only the runtime payload and notices into the scratch image.
Keep source tags literal in `package`; set `sql` to the version actually declared
by the extension, and configure root Renovate rules for verified mappings.

Unlike PGRX's Cargo helpers, Universe has no general dependency-discovery or
license-collection helper. Each recipe must identify its bundled/static runtime
components, stage required libraries and original notices, and provide evidence
for the shared generator. The template's `acquire.py`, `evidence.py` and
`augment_spdx.py` names are examples of recipe-owned files, not supplied utilities.
Use inline Dockerfile commands where sufficient; do not create scripts just to
match the example names.

Preserve the generator's OS package ownership and shipped-file inventory. A hook
adds source-built packages with accurate names, versions or revisions, dependency
relationships and licenses; it does not replace the generator. Runtime components
and bundled data must meet the [licensing policy](../../README.md#open-source-licensing-policy).
Build-only dependencies must not be reported as part of the distributed payload.

See the [shared source-build guide](../README.md) for dependency evidence,
local builds, tooling tests and image verification.
