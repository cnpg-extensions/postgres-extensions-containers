# Source-build utilities

These utilities prepare and assemble native PostgreSQL extension builds. Recipes
live under `pgrx/<name>` and `universe/<name>`; directory location determines the
build family. Shared tools live here, while Rust-specific tools live in `pgrx/`.

Use the [PGRX recipe guide](../pgrx/README.md) for Rust extensions and the
[Universe recipe guide](../universe/README.md) for other source builds. The
[repository build guide](../BUILD.md) covers the shared Task/Dagger commands.

## Add a Universe recipe

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
  "$SBOM_GENERATOR" source-build/pgrx/test.py
```

The runner discovers both shared and PGRX tests, including preparation, native
assembly and generator/hook composition. Recipe evidence tests should cover lost
packages, identifiers, notices and payload ownership. Universe's evidence is
recipe-specific and must be reviewed when upstream components change.

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
