# Universe recipe development

Universe is for extensions with complex dependency packaging or unresolved
maintenance and delivery requirements that prevent using Debian/PGDG packages
on the supported targets. Prefer Debian packaging when available; Rust source
builds use PGRX. Document the specific obstacles and shipped-component evidence in
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
for the shared generator. Acquire sources over trusted upstream HTTPS in the
Dockerfile, using archives or Git checkouts and the selected release's nested
dependencies. The template's `augment_spdx.py` is a recipe-owned hook, not a
supplied utility. Use inline commands for notice and runtime-file staging where
sufficient; no separate evidence script is required.

Preserve the generator's OS package ownership and shipped-file inventory. A hook
adds source-built packages with accurate names, versions or revisions, dependency
relationships and licenses; it does not replace the generator. Runtime components
and bundled data must meet the [licensing policy](../README.md#open-source-licensing-policy).
Build-only dependencies must not be reported as part of the distributed payload.

See the [shared source-build guide](../README.md) for dependency evidence,
local builds, tooling tests and image verification.

README image and SQL examples use Renovate annotations matching metadata
(`datasource`, `depName`, and `versioning`), with `depType=universe-source`.
The shared README rule removes a leading `v` from release versions and preserves
the image's PostgreSQL/distribution suffix. Annotate SQL examples only when their
release-version mapping is verified. Keep historical investigation versions fixed.

## Review checklist for new recipes and updates

Record recipe-specific evidence and limitations in `PACKAGING.md`; keep this
checklist as the shared review entry point. Revisit it when source versions,
bundled dependencies, build flags or the pinned SBOM generator change.

- **Payload and boundaries:** justify the Universe packaging choice, identify
  source-built and system runtime components (including static code and data),
  and explain package boundaries. Verify versions against the selected source
  and compiler settings. Exclude build-only tools and runtime downloads.
- **Original notices:** retrieve `/licenses` from the final image. Check complete
  upstream notices, bundled-component attribution and any referenced common
  license texts against the selected sources. Reassess checked-in copyright
  snapshots on updates; a successful build does not establish their coverage.
- **SBOM conventions:** compare the hook's output with the pinned shared
  generator and an existing extension. Preserve standard license expressions,
  existing license records, file ownership and checksums. For notice references
  without embedded text, use the generator/Syft `extractedText: "NOASSERTION"`
  convention, with original text shipped under `/licenses` and explicit package
  relationships to the inventoried notice files. Every `LicenseRef` must resolve;
  do not remove its record or replace package attribution with `NOASSERTION`
  merely to avoid embedding text. Do not rewrite generator-owned license text.
- **Regression coverage:** exercise the recipe hook in the existing
  `source-build/tests` suite. Check complete package/notice relationships,
  unchanged inventory and checksums, resolved license references, and missing
  notice failures. Assert the intended consumer-visible evidence, rather than
  fixed package counts or the hook's current serialization alone.
- **Real output:** use the [shared build and verification commands](../README.md#local-builds)
  to inspect attached SPDX and extract notices for every supported distribution
  and architecture. Check notice hashes against the final image, run the shared
  scans and runtime smoke tests, and retain the normal signing/SLSA release
  gates. Report exactly which checks ran, distinguishing fixture tests, reused
  compiled builders, fresh native builds and hosted acceptance.

The [pg_duckdb packaging notes](../../universe/pg-duckdb/PACKAGING.md) illustrate
where to record component boundaries and notice provenance. Its
[hook tests](../tests/test_universe_hook.py) cover notice references without
embedded text and preservation of the shared inventory.
