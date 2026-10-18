# SBOM generator reviewer guide

The final image is built `FROM scratch`: it retains extension files and libraries,
but no package database. The generator uses the builder's package evidence to
identify the files actually shipped, excluding packages with no matched files.
It runs as a BuildKit scanner; its tools are not added to the extension image.

The first PR adds the generator image, publication workflow, composer, hook, and
checks. This adoption PR connects extension builds to that generator and adds the
end-user documentation. PGRX follows as a separate downstream consumer.

See [How it works](README.md#how-it-works) for the complete architecture diagram.

Files are copied to different locations in the scratch image: for example,
`/usr/share/doc/gcc-12-base/copyright` becomes `/licenses/gcc-12-base/copyright`.
The final path therefore cannot be used directly to look up Debian ownership.
We match each shipped file to its original builder file, then retain the package
that owned that builder file.

Ownership requires matching SHA256 content. Exact paths and shared path suffixes
rank candidates; ambiguous matches stay unclaimed. The composer retains owning
packages and their relationships, preserves Syft package identities, and merges
license evidence. It does not infer ownership from a license-directory
name. Large copyright files are split for scanning, then findings are mapped back
to their original file paths.

## Where to review

| Area | Entry points |
| --- | --- |
| Scanner lifecycle, final inventory, ScanCode invocation, BuildKit statement | [generator.py](generator.py) |
| File ownership, package selection, license composition, document identity | [compose.py](compose.py) |
| Optional hook and its context | [hooks.py](hooks.py) |
| Final SPDX conformance check | [spdx_validation.py](spdx_validation.py), [release constraints](Dockerfile) |
| Scanner image and dependencies | [Dockerfile](Dockerfile) |
| Extension integration | [docker-bake.hcl](../docker-bake.hcl), [bake_targets.yml](../.github/workflows/bake_targets.yml) |
| Generator checks, publication, and digest updates | [sbom-generator.yml](../.github/workflows/sbom-generator.yml), [release.py](release.py), [renovate.json](../renovate.json) |
| Unit checks and real BuildKit/SPDX/Grype/Grant fixture | [tests](tests), [integration](tests/integration) |

CI selects the scanner and inserts `ARG BUILDKIT_SBOM_SCAN_STAGE=builder` into
the Dockerfile so BuildKit exposes the builder stage. The scanner is pinned to
the checked official image digest in `bake_targets.yml`. Ordinary local Bake builds use the
default scanner when `sbom_generator` is empty. BuildKit produces detailed provenance (`mode=max`);
the SLSA reusable workflow adds signed provenance for each published index.
Testing provenance gates production copying; production provenance is generated at the destination.
The generator wraps its SPDX in an in-toto statement; BuildKit attaches it to the
image. Signing and SLSA provenance are handled separately by the workflows.

## Downstream augmentation

A builder may supply `/usr/local/share/cnpg-sbom/augment_spdx.py` with
`augment_spdx(document, context) -> dict`. The hook runs after composition and
before validation. [HookContext](hooks.py) exposes API version 1, extension name,
platform, builder/final paths, and the complete Syft builder document.

The hook executes trusted Python in the generator environment. Builder-installed
dependencies are unavailable there; downstream builds can prepare JSON evidence
for the hook to read. Missing hooks leave the document unchanged; hook errors or
invalid final SPDX fail the build. SPDX validation checks conformance, not whether
added components actually belong to the payload.

PGRX is a downstream consumer of this interface: it supplies Cargo component and
license evidence. The core generator has no Cargo or PGRX processing dependency.
The [fixture hook](tests/integration/fixture/augment_spdx.py) demonstrates adding
a package that Grant can report.

## Local checks

From the repository root:

```bash
docker build -t cnpg-sbom-generator:local sbom-generator
docker run --rm --entrypoint python3 \
  --volume "$PWD:/workspace:ro" --workdir /workspace \
  cnpg-sbom-generator:local -m unittest discover -s sbom-generator/tests

# Extract an SPDX document for the validator check below.
IMAGE=ghcr.io/cnpg-extensions/pgsphere@sha256:54e6f0b0a9d9e4c80db8c6edcac98b451159c1fbaa91e429a92d4978f593518d
docker buildx imagetools inspect "$IMAGE" \
  --format '{{ json (index .SBOM "linux/amd64").SPDX }}' \
  > pgsphere-amd64.spdx.json
docker run --rm --entrypoint python3 --volume "$PWD:/workspace:ro" \
  cnpg-sbom-generator:local /opt/cnpg-sbom-generator/spdx_validation.py \
  /workspace/pgsphere-amd64.spdx.json
```

Delete `pgsphere-amd64.spdx.json` after the check, or supply another extracted
SBOM at that path. See the [user guide](README.md#verify-the-image-and-extract-its-sbom)
for publisher verification.

The validator accepts extracted SPDX or the generator's in-toto statement and
exits nonzero on invalid output. Native AMD64 and ARM64 CI checks also build the
scanner and exercise a real BuildKit attestation, Debian notice ownership, hook
augmentation, Grype distribution detection, and Grant license reporting.

See the [user and release guide](README.md) for inspection and publication commands.

## Release promotion

The generator image itself includes BuildKit's default SBOM and detailed
provenance, and the workflow signs its checked digest with Cosign. This does not
use the extension images' separate SLSA reusable workflow.

The publish job is serialized. Once its digest passes checks, a `main` push
updates `latest` even if unrelated commits have since advanced `main`.
`release.py` verifies the immutable commit tag and promoted alias against the
checked digest. GitHub does not guarantee queue order, so serialization alone
does not enforce source-commit order for publications.
