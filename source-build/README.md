# Source-build utilities

These utilities prepare and assemble native PostgreSQL extension builds. Recipes
live under `pgrx/<name>` and `universe/<name>`; directory location determines the
build family. Shared tools live here, while Rust-specific tools live in `pgrx/`.

Use the [PGRX recipe instructions](#add-a-pgrx-recipe) for Rust extensions and the
[Universe recipe instructions](#add-a-universe-recipe) for other source builds. The
[repository build guide](../BUILD.md) covers the shared Task/Dagger commands.

## Add a PGRX recipe

PGRX recipes are discovered from `pgrx/<extension>/metadata.hcl`. Directory location selects the PGRX build family.

**Start from the [PGRX templates](pgrx/templates/) and follow their structure.**
The [Dockerfile template](pgrx/templates/Dockerfile.tmpl) contains the integration
points used by CI, native builds, and SBOM generation. Adapt the source URL,
upstream build commands, dependencies, and copied runtime files for the extension;
keep the shared setup and evidence steps.

For a new extension:

1. Copy and complete the Dockerfile, metadata, and README templates, replacing
   every placeholder and TODO. Set the canonical source repository in the
   Dockerfile and the literal source tag in metadata, including a leading `v`
   when upstream uses one.
   Set `sql` to the tag without a leading `v`, immediately below `package` so
   Renovate updates both together.
2. Preserve all Dockerfile `ARG` declarations **in their template locations and
   stages**, including `BUILDKIT_SBOM_SCAN_STAGE`, `BASE`, `PG_MAJOR`, `EXT_VERSION`,
   `TARGETARCH`, `TARGETPLATFORM`, `PGRX_EXTENSION`, `PGRX_DISTRO`, and
   `PGRX_BUILD_TIMESTAMP`. They pass CI's selected versions, architecture, source
   selection, and timestamp into the build and evidence tools. Some are consumed
   by helper scripts rather than referenced directly in the Dockerfile. Docker
   arguments are stage-scoped, so retain repeated declarations such as `PG_MAJOR`
   in the final stage too.
3. Keep the stage named `builder`, copy `source-build/` to `/source-build/`, and extract the source
   into `/build`. **Call `/source-build/pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}"
   /build/Cargo.lock` after extraction and before compilation.** It installs the
   build environment, selects cargo-pgrx from the source lockfile, and prepares
   the SBOM hook and reporting tools.
4. Add the extension to `RECIPES` in [`build_config.py`](pgrx/build_config.py), matching
   the Dockerfile's manifest path, features, and package/install layout. Add any
   required apt dependencies and keep the upstream recipe URL immediately above
   the build commands.
5. **Call `/source-build/pgrx/finalize-pgrx-evidence.sh` after compilation and packaging.** It
   records the completed payload and generates Cargo and license evidence needed
   by the SBOM hook. Preserve the diagnostic `pgrx-sbom` stage and copy the
   generated Rust license notices into the final image alongside the runtime
   files, as the template shows.
6. Declare supported distribution/PostgreSQL combinations in metadata;
   preparation creates their native build jobs automatically. Run the shared
   [local builds and checks](#local-builds). Use the existing SBOM generator
   and hook; do not add a second composer or a build-system-specific consumer
   interface.

In the extension README, explain SQL and catalog names, preload requirements,
and any initialization steps.

### Recipes with additional runtime needs

Recipes that need additional OS runtime libraries capture base libraries before
installing packages, then stage the packaged extension's additional runtime
closure and copyright notices using the shared helpers. pg-search 0.26.6 uses
LLD and OpenBLAS at build time but does not stage additional runtime libraries.

PostgreSQL Anonymizer declares its GitLab source URL in its Dockerfile and
uses the upstream `make extension` target, including runtime CSV data. Payload
evidence includes that data directory recursively. Its catalog preloads `anon`;
initialize its legacy fake-data functions with the mounted data path described
in the extension README.

### PGRX source updates

Renovate PGRX source and build-tool updates inherit the shared minor, patch and
digest automerge policy, subject to required checks. Major updates remain manual.
Renovate updates `package` and the adjacent `sql` value together for every PGRX
extension, stripping only a leading `v` from the source tag for SQL. If upstream
ships a different SQL version, investigate the release before merging.

## Add a Universe recipe

Universe is for extensions whose dependency burden makes Debian packaging
prohibitive. Ordinary extensions should use Debian packaging; Rust extensions
use PGRX. Document the specific obstacles and shipped-component evidence in
`PACKAGING.md`.

Start from the [Dockerfile, README and metadata templates](universe/templates/).
They use the existing scaffolder and do not require a separate generator:

```sh
dagger call -sm ./dagger/maintenance/ create \
  --name=my-extension --versions=18 --distros=trixie \
  --templates-dir=./source-build/universe/templates \
  export --path=./universe/my-extension
```

Replace all TODOs and placeholders. Follow the [pg-duckdb recipe](../universe/pg-duckdb/)
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
and bundled data must meet the [licensing policy](../README.md#open-source-licensing-policy).
Build-only dependencies must not be reported as part of the distributed payload.

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

### PGRX Bake targets

Use the extension's ordinary Bake targets with
`-f docker-bake.hcl -f docker-bake-pgrx.hcl -f pgrx/<extension>/metadata.hcl`
in that order. Supply `build_timestamp` and the digest-qualified `sbom_generator`
from preparation. Select explicit named Bake targets to build a single local
distribution, and restrict the platform to your host's native architecture
(for example, `--set '*.platforms=linux/amd64'` on AMD64). Do not emulate the
other architecture for a Rust build.

The diagnostic `pgrx-sbom` target exports Cargo evidence for inspection. It does
not replace an image build that produces attestations or test hosted signing.

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
| [`pgrx/`](pgrx/) | Rust installers, Cargo evidence, SBOM hook, templates and tests. |
| [`universe/templates/`](universe/templates/) | Dockerfile, user README and metadata templates for Universe recipes. |

### PGRX tools

Extension-specific Dockerfiles and metadata live under `pgrx/<extension>/`. Rust-specific
tools live under `source-build/pgrx/`:

| File or directory | Purpose |
| --- | --- |
| [`build_config.py`](pgrx/build_config.py) | Registers extension recipes and their Cargo feature selection. |
| [`install-pgrx-build-environment.sh`](pgrx/install-pgrx-build-environment.sh) | Required Dockerfile setup step: installs build tools and the SBOM hook. |
| [`finalize-pgrx-evidence.sh`](pgrx/finalize-pgrx-evidence.sh) | Required post-build step: collects Cargo, license, and runtime-payload evidence. |
| [`templates/`](pgrx/templates/) | Dockerfile, metadata, and README templates to follow for new extensions. |
| [`sbom/`](pgrx/sbom/) | Hook that adds verified Rust dependencies and licenses to the shared generator's SPDX output. |
| [`dependencies/`](pgrx/dependencies/) | Rust, rustup, and cargo-about version configuration for extension builders. |
| [`tests/`](pgrx/tests/) | PGRX tests, run with `python3 source-build/test.py`. |
