# Source-build utilities

These utilities prepare and assemble native PostgreSQL extension builds. Recipes
live under `pgrx/<name>` and `universe/<name>`; directory location determines the
build family. Shared tools live here, while Rust-specific tools live in `pgrx/`.

Use the [PGRX recipe instructions](pgrx/README.md) for Rust extensions and the
[Universe recipe instructions](universe/README.md) for other source builds. The
[repository build guide](../BUILD.md) covers the shared Task/Dagger commands.

## Dependency evidence in the SBOM

The final SPDX SBOM must include shipped dependencies, including bundled and
statically linked components that automatic scanning misses. Each dependency
must use its canonical upstream or ecosystem package name, including the name
used by vulnerability advisories where applicable. This matters even when no CVE
exists today: future advisories should be matchable to the shipped component.
Do not substitute a recipe-local nickname for an established package identity.
Matching still depends on scanner and advisory support. Unknown versions can
broaden scanner matches as well as reduce coverage; missing identifiers can also
limit automated matching.

Use established SPDX fields and Package URL types:

- Record the actual upstream version when known. A source-declared version can
  be a useful, explicit approximation for a fork, as in the PGRX example below.
  When no defensible version is available, omit optional `versionInfo`; do not
  invent versions from repository commits and source paths. Distinguish source
  versions from API compatibility macros.
- Include an accurate standard PURL when the component's ecosystem and source
  support one. Do not guess registry membership, CPEs, versions or identifiers
  merely to satisfy a scanner. Preserve canonical names when a reliable PURL is
  unavailable, and explain unresolved identity evidence in the recipe's packaging notes.
- Express dependency relationships using standard SPDX relationships. Keep
  distinct components distinct, including forks with the same name and version.
- Preserve shipped-file inventory, runtime package ownership, checksums, license
  expressions and original attribution/notices. Use SPDX `LicenseRef` and
  extracted licensing information for terms without an applicable SPDX license
  identifier. Associate required redistribution notices with the standard
  `DISTRIBUTION_ARTIFACT` relationship.

Use the shared generator's existing augmentation hook for missing source-built
components. Evidence must describe the selected sources and final payload;
validate their binding during the build. Builder reports and recipe helpers are
private implementation details, not a second consumer schema. Do not publish
custom JSON annotations, identifier qualifiers, sidecars or attestations as an
alternative API. SPDX identifiers and document namespaces are opaque;
`sourceInfo` is optional human-readable context, not a parseable contract.

Source attribution remains available through recipes, standard source links and
ordinary build provenance where captured. Exact source commit recovery is not a
prerequisite for every build. Tags may move and acquisition may be cached; a
build timestamp alone does not prove which commit a tag selected. Recipes may
resolve commits privately when required to acquire matching nested dependencies.
This does not introduce a new public source-identity contract.


### Example: pg-search's Rust dependencies

The pg-search 0.26.6 dependency graph includes Git forks of published Rust crates.
Their Cargo package names are the identities used by RustSec and OSV advisories;
repository names and dependency aliases are not substitutes. For example, the
pinned Tantivy source declares package `tantivy` version `0.27.0`, so its standard
PURL is `pkg:cargo/tantivy@0.27.0`. The fact that the source comes from ParadeDB's
fork does not change the canonical crate name used for vulnerability matching.

We intentionally use the version declared by the selected source as an
approximation. A fork may include unreleased fixes or changes, so this can yield
false positives or false negatives. Searching Git history for the latest
published ancestor is not necessarily a better approximation: the inspected
Tantivy fork declares `0.27.0`, but the highest stable, non-yanked release with an
ancestor publication commit was `0.19.0`, because later release commits were on
other branches. We preserve useful ecosystem identity without claiming exact
release equivalence or inventing commit-based versions and PURL qualifiers.

The PGRX helpers implement this policy deliberately:

- [`evidence.py`](pgrx/evidence.py) obtains resolved package names and declared
  versions from `cargo metadata`. For selected Git dependencies, it checks that
  the exact name/version exists on crates.io and retains the registry's version
  records as private build evidence. Repeated identities share a lookup. A
  missing release is omitted from these records; registry service errors fail
  the build rather than silently removing PURLs.
- [`augment_spdx.py`](pgrx/sbom/augment_spdx.py) runs offline and emits standard
  Cargo PURLs for crates.io dependencies and the confirmed Git identities.
  Package identity comes from Cargo's package fields, not an alias or repository
  basename. Registry membership confirms an identity, not source equivalence.
- The two Git copies of `superkmeans-rs` both declare `0.3.0`, so both use
  `pkg:cargo/superkmeans-rs@0.3.0`, while retaining separate SPDX components and
  dependency relationships. Unpublished `tantivy-quant` remains named and
  versioned without claiming a crates.io PURL. Workspace packages and alternate
  registries are not automatically mapped to crates.io.

This is PGRX's automatic implementation of the shared evidence principle.
Universe recipes must establish their own ecosystem identities and defensible
versions; the Cargo lookup policy does not apply to DuckDB's dependencies. The
published output remains ordinary SPDX and Package URLs, with no additional
consumer schema or API.

## Local builds

Run from the repository root with Docker/Buildx and Python 3. Use a local registry
so pushed images retain their SBOM and provenance attestations. Select a native
AMD64 or ARM64 Docker-container builder; host, daemon and worker must agree.

Set `SBOM_GENERATOR` to the repository's current digest-qualified shared generator
image. Preparation takes a recipe name and family:

```sh
printf '%s\n' '{"extension_name":"pg-duckdb","build_family":"universe"}' > /tmp/source-inputs.json
GITHUB_RUN_ID=local registry=localhost:5000 \
  python3 source-build/prepare.py --inputs /tmp/source-inputs.json \
  --generator "$SBOM_GENERATOR" --output /tmp/source-prepared
python3 source-build/build.py --architecture amd64 --builder NAME
```

`GITHUB_RUN_ID` is the preparation tool's build identifier; `local` is sufficient
for a local run. Use a fresh output directory for each preparation. The resulting
`preparation.json` lists each distribution/PostgreSQL/platform row and its Bake
file. Choose the row matching the local architecture and intended target:

```sh
docker buildx bake --builder NAME \
  -f /tmp/source-prepared/ROW.json TARGET
```

Use `arm64` for an ARM64 worker. Never compile a source recipe under emulation.
For PGRX, select `build_family=pgrx`; the preparation tool supplies its Rust-specific
arguments. The shared [local smoke-test instructions](../BUILD.md#local-testing-guide)
accept logical names such as `pg-duckdb`. Universe uses the ordinary installation
and version checks; no separate extension-specific runtime suite is required.

## Tooling tests

Run the existing suite in the pinned generator image so its Syft, SPDX validator
and composer match the build environment:

```sh
docker run --rm --entrypoint python3 \
  --volume "$PWD:/workspace:ro" --workdir /workspace \
  "$SBOM_GENERATOR" source-build/test.py
```

The runner discovers both shared and PGRX tests, including preparation, native
assembly and generator/hook composition. Recipe evidence tests should cover lost
packages, identifiers, notices and payload ownership. Universe's evidence is
recipe-specific and must be reviewed when upstream components change.

The shared runner and files under `source-build/tests/` are listed below. These
checks use fixtures and mocked external commands; they do not build extensions
or run PostgreSQL.

| Test file | Implementation tested | Coverage |
| --- | --- | --- |
| [`test.py`](test.py) | Runs [`tests/`](tests/) and [`pgrx/tests/`](pgrx/tests/) | Shared entrypoint: discovers both suites, rejects empty PGRX discovery and exits unsuccessfully if any test fails. |
| [`test_discovery.py`](tests/test_discovery.py) | [`workflow.py`](workflow.py) | Location-derived families, recipe boundaries, duplicate names and wrong-family selections. |
| [`test_inputs.py`](tests/test_inputs.py) | [`source.py`](source.py), [`prepare.py`](prepare.py) | GitLab source resolution and architecture-specific base-image selection. |
| [`test_native_builds.py`](tests/test_native_builds.py) | [`prepare.py`](prepare.py), [`build.py`](build.py) | Separate native-platform build definitions and rejection of mismatched host, daemon or worker architectures. |
| [`test_assembly.py`](tests/test_assembly.py) | [`assemble.py`](assemble.py) | Complete platform coverage and preservation of image and attestation descriptors during assembly. |
| [`test_registry.py`](tests/test_registry.py) | [`assemble.py`](assemble.py) | Waiting for the expected registry index digest and rejecting stale or different index contents. |
| [`test_universe_hook.py`](tests/test_universe_hook.py) | [`pg-duckdb/evidence.py`](../universe/pg-duckdb/evidence.py), [`pg-duckdb/augment_spdx.py`](../universe/pg-duckdb/augment_spdx.py) | pg-duckdb dependency identities, vendor versions, notice preservation, payload binding and preservation of existing SBOM records. |

## Verify images

Follow the SBOM guide to [verify the image and extract its
SBOM](https://github.com/cnpg-extensions/cnpg-sbom-generator#verify-the-image-and-extract-its-sbom),
[inspect and verify build provenance](https://github.com/cnpg-extensions/cnpg-sbom-generator#inspect-and-verify-build-provenance),
and [report vulnerabilities and licenses](https://github.com/cnpg-extensions/cnpg-sbom-generator#report-vulnerabilities-and-licenses).
The tools listed in that guide are sufficient; no source-build toolchain is needed.

For images published by `cnpg-extensions` from `main` through the shared source
workflow, use this exact `--certificate-identity` in the guide's Cosign command:

```text
https://github.com/cnpg-extensions/postgres-extensions-containers/.github/workflows/source-build-targets.yml@refs/heads/main
```

For older PGRX images published through `pgrx_targets.yml`, use their original
signing identity instead:

```text
https://github.com/cnpg-extensions/postgres-extensions-containers/.github/workflows/pgrx_targets.yml@refs/heads/main
```

Keep the guide's GitHub Actions OIDC issuer and add
`--new-bundle-format=false` for this repository's legacy-format signatures.
For another publisher, change both the image repository and the exact workflow
identity to that publisher's repository and trusted branch. After copying an
image, verify the destination repository's signature as well.

The guide's extraction examples use a multi-platform index. For a
single-platform index, confirm its platform with `docker buildx imagetools
inspect`, then use `.SBOM.SPDX` and `.Provenance.SLSA` in the format expressions.

PGRX and Universe use the same published SBOM format and consumer tools as Debian
extensions. Scan the PostgreSQL base image separately using its own SBOM.

## Directory guide

| File or directory | Purpose |
| --- | --- |
| [`prepare.py`](prepare.py) | Turns metadata into native build rows and Bake definitions. |
| [`workflow.py`](workflow.py) | Discovers source recipes and their location-derived families. |
| [`build.py`](build.py) | Checks native host, daemon and BuildKit-worker architecture. |
| [`assemble.py`](assemble.py) | Combines platform images and preserves attestations. |
| [`source.py`](source.py) | Shared source-resolution helpers. |
| [`tests/`](tests/) | Shared tooling and recipe-hook tests. |
| [`pgrx/`](pgrx/README.md) | Rust installers, Cargo evidence, SBOM hook, templates and tests. |
| [`universe/`](universe/README.md) | Recipe-authoring guide and templates for Universe builds. |
