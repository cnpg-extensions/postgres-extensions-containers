# Shared source builds

PGRX and Universe recipes share native AMD64/ARM64 builds, SBOM generation,
signing, security checks, CloudNativePG smoke tests and release provenance.
Recipes live in `pgrx/<name>` and `universe/<name>`; this directory contains the
shared orchestration and family-specific tools. Location determines build family.
The legacy PGRX `build_system` metadata field is ignored.

Start with the extension's README for SQL names, preload settings and
initialization. Recipe authors should also read the [PGRX guide](../pgrx/README.md)
or [Universe guide](../universe/README.md).

Published images include software bills of materials, build provenance and
original license notices. They use the same consumer tools as Debian-built
extensions. All distributed components must meet the
[Open Source Licensing Policy](../README.md#open-source-licensing-policy).
Scan the PostgreSQL base image separately using its own SBOM.

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

## How images are built

[`source-build.yml`](../.github/workflows/source-build.yml) selects extensions and calls
[`source-build-targets.yml`](../.github/workflows/source-build-targets.yml) for each one.
`prepare.py` turns the extension's `metadata.hcl` into a build plan. Each
**target** is one distribution/PostgreSQL combination; each target gets separate
AMD64 and ARM64 jobs on matching native runners.

The boxes below distinguish runner hosts from the containers they launch.
Solid arrows show data flow or required completion. Dashed arrows show reusable
workflow calls, positioned after the jobs they depend on; these calls are
scheduled by GitHub Actions, not made by the Python scripts. Smoke and SLSA
workflows manage their own jobs and runners.

```mermaid
flowchart TD
    Entry["source-build.yml"] -. "calls source-build-targets.yml" .-> Prepare

    subgraph PrepRunner["Preparation runner"]
        Prepare["prepare.py"]
    end

    subgraph AMD["AMD64 runner — per target"]
        AB["build.py + Docker Bake"]
        subgraph AC["BuildKit-managed containers"]
            AX["Build extension → finalize evidence"]
            AG["SBOM generator + recipe hook"]
            AX --> AG
        end
        AB --> AX
    end

    subgraph ARM["ARM64 runner — per target"]
        RB["build.py + Docker Bake"]
        subgraph RC["BuildKit-managed containers"]
            RX["Build extension → finalize evidence"]
            RG["SBOM generator + recipe hook"]
            RX --> RG
        end
        RB --> RX
    end

    subgraph Assembly["Assembly runner"]
        Assemble["assemble.py + Cosign<br/>Merge and sign"]
    end

    subgraph Security["Security runner — per image"]
        Scan["Shared security-scans action<br/>Dockle + optional Snyk"]
    end

    Smoke["Reusable smoke.yml<br/>Jobs per image / CNPG version"]
    SLSA["Reusable SLSA workflow<br/>Testing provenance"]

    subgraph Promotion["Promotion runner — main only"]
        Promote["copy-images action"]
    end

    ProdSLSA["Reusable SLSA workflow<br/>Production provenance"]

    Prepare --> AB
    Prepare --> RB
    AG -->|"Image + digest metadata"| Assemble
    RG -->|"Image + digest metadata"| Assemble
    Assemble --> Scan
    Assemble -. "workflow call" .-> Smoke
    Assemble -. "workflow call" .-> SLSA
    Scan -->|"Job must succeed"| Promote
    Smoke -->|"Must pass"| Promote
    SLSA -->|"Must pass"| Promote
    Promote -. "workflow call" .-> ProdSLSA
```

On each native runner, `build.py` checks the architecture before Docker Bake
starts the build. Inside the build containers, the extension's Dockerfile
installs tools, runs the upstream build recipe, finalizes source and license
evidence, and copies runtime files into a minimal `scratch` image. The shared
[SBOM generator](https://github.com/cnpg-extensions/cnpg-sbom-generator#consumer-integration) runs in its own container;
the family or recipe hook adds selected source-built packages and license
information to its SPDX 2.3 document. BuildKit attaches the SBOM and build
provenance to the platform image.

The build jobs push their images to the registry and pass digest metadata through
workflow artifacts. On a separate runner, `assemble.py` combines both platforms
and checks that every image and attestation descriptor survives unchanged.
Cosign signs the assembled index. Later jobs use its immutable digest.

Security, smoke tests, and testing-image SLSA provenance can then run in parallel.
The security runner uses the same shared `security-scans` action as mainline.
Dockle checks image configuration and fails on warnings or errors. When
`SNYK_TOKEN` is configured, Snyk scans the image and uploads findings to GitHub
Code Scanning; the Snyk step is allowed to fail without blocking the job.
This action does not explicitly scan both platform SBOMs or produce Grant
license reports. Both SBOMs remain attached to the image for consumers to scan
against current vulnerability databases using the [verification guide](#verify-images).
Build-time SPDX validation remains in place. The shared smoke workflow tests the
extension in CloudNativePG, and the shared SLSA workflow separately attests the
testing image's build provenance.

Branch builds publish testing images. After all required checks succeed, trusted
`main` push or dispatch events can run the shared `copy-images` action on the
promotion runner. It copies the checked images to production and signs their
digests. A final SLSA workflow call attests the production images in their
destination repositories.

## Development

### Test a complete extension build

For full extension acceptance, dispatch
[`.github/workflows/source-build.yml`](../.github/workflows/source-build.yml) with an
`extension_name`. It builds all targets declared in the extension's metadata on
native AMD64 and ARM64 runners, assembles and signs their indexes, checks
SPDX output, runs mainline security checks, and runs CNPG smoke tests. An optional `cnpg_version`
selects `main` or a full version such as `1.30.1`; otherwise the shared support
policy selects the smoke versions. No local signing keys are needed.

Debian, PGRX and Universe use the shared [smoke workflow](../.github/workflows/smoke.yml)
and test the same CNPG versions: `main`, the highest stable patch of the previous
minor, and the pinned latest release. Smoke uses the standard Task/Dagger setup,
CNPG extension catalogs, and extension installation checks. The source pipeline
supplies the assembled image digest and selected CNPG release directly. The shared Taskfile
uses live operator manifests and catalogs, including development images for
`main`.

### Try an unsigned local build

Use a local registry to preserve BuildKit SPDX and provenance attestations.
Create a Docker-container Buildx builder, then run
`python3 source-build/build.py --architecture amd64 --builder NAME` (or `arm64` on ARM). Host, daemon and worker must agree.
Preparation accepts JSON containing `extension_name` and `build_family`:

```sh
GITHUB_REPOSITORY_OWNER=cnpg-extensions GITHUB_RUN_ID=local registry=localhost:5000 \
  python3 source-build/prepare.py --inputs /tmp/inputs.json \
  --generator "$SBOM_GENERATOR" --output /tmp/prepared
```

Take `SBOM_GENERATOR` from `source-build-targets.yml`. Select only the prepared
rows for the native architecture and intended distribution, then invoke
`docker buildx bake --builder NAME -f /tmp/prepared/ROW.json TARGET` with the
explicit prepared target name. Do not build a foreign row under emulation.

Run the ordinary `task e2e:setup-env`, `task e2e:generate-values`,
`task e2e:export-kubeconfig` and `task e2e:test` commands with the logical TARGET
and the test image reference. The existing shared harness loads the tested image
and runs installation/version checks. Existing recipe suites also run when
present; Universe requires no separate suite.

### Local validation

The [source-build tooling test workflow](../.github/workflows/source-build-tests.yml) is called by the
shared source-build workflow and can also be dispatched separately. Its contract tests
are required by the `Source-build acceptance` gate; Go tests remain independent.
These tests exercise shared preparation, assembly and SBOM composition, along
with family-specific evidence handling.

Both build workflows report their local gates on every pull request,
merge-queue commit, and push to `main`. Discovery selects the extensions to
build; shared changes select the [representative sample](../BUILD.md#usage-and-targets)
on PRs, while only payload changes rebuild automatically on `main`. An empty
selection skips builds explicitly. Failed discovery, contract
tests, or unexpectedly skipped acceptance jobs fail the relevant gate.
Branch protection should require both `Automerge gate` (Debian) and
`Source-build acceptance`. Configure these checks after their first runs; changing the
workflow files does not change repository rules. Mixed Debian/source changes run the applicable build workflows.
For a working branch without a pull request, dispatch the relevant build workflow.
Use `extension_name=all` to rebuild every extension in that workflow.
The source selector discovers `pgrx/<name>` and `universe/<name>` recipes and
carries each recipe's family into its build matrix.

Renovate tracks source versions and build inputs in the root configuration.
Automerge eligibility depends on the matching package rules and required checks;
SQL mappings and source evidence must remain valid for the selected release.

The release acceptance jobs publish testing images and require registry write
and signing permissions. Fork PRs use the
[maintainer-authorized test path](../WORKAROUNDS.md#ci-authorized-testing-of-fork-prs);
ordinary fork builds and preview gates are skipped. Authorized runs report the
required statuses directly on the tested head SHA.

Run from the repository root with Docker, bash, jq, Python 3, and actionlint available. Run the
downstream suite inside the pinned generator image, matching CI's Syft,
SPDX validator, and composer:

```sh
generator=$(sed -n 's/^ *SBOM_GENERATOR: //p' .github/workflows/source-build-tests.yml)
test -n "$generator"
docker run --rm --entrypoint python3 \
  --volume "$PWD:/workspace:ro" --workdir /workspace \
  "$generator" source-build/pgrx/test.py

actionlint .github/workflows/bake.yml \
  .github/workflows/bake_targets.yml \
  .github/workflows/source-build.yml \
  .github/workflows/source-build-targets.yml \
  .github/workflows/source-build-tests.yml \
  .github/workflows/cnpg-versions.yml \
  .github/workflows/smoke.yml
```

The suite covers shared preparation and native-platform assembly, plus
family-specific package selection, licenses, ownership, shipped files and
generator/hook composition. Shared Go tests have their own workflow.

The generator source, release workflow, and BuildKit/SPDX/Grype/Grant integration
fixtures are maintained in the [external generator repository](https://github.com/cnpg-extensions/cnpg-sbom-generator).
Debian, PGRX and Universe builds consume its published `latest` image with an immutable
digest; Renovate groups updates to the workflow pins.

## Discovery and catalogs

`get-targets` defaults to Debian. Use `--build-system pgrx`,
`--build-system universe`, or `--build-system all` to select source families or all recipes.
Logical targets such as `pg-duckdb` resolve to their recipe directories. Source
recipes are excluded from Debian OS-library package maintenance; their builders
stage the runtime libraries and notices they need.

Catalog generation includes all three families through the existing image lookup,
upstream precedence and publication workflow. Repository maintainers maintain all
extensions. Fork tests use the trusted base `maintainer-pr-tests.yml` workflow,
which accepts repository Write, Maintain or Admin permission under its existing
actor/rerun checks. Same-repository PRs and manual dispatches use the normal
workflow entrypoints.

## Directory guide

| File or directory | Purpose |
| --- | --- |
| [`prepare.py`](prepare.py) | Turns metadata into native build jobs and Bake definitions. |
| [`workflow.py`](workflow.py) | Discovers source recipes and their location-derived families. |
| [`build.py`](build.py) | Checks native host, daemon and BuildKit-worker architecture. |
| [`assemble.py`](assemble.py) | Combines platform images and preserves attestations. |
| [`source.py`](source.py) | Shared source-resolution helpers. |
| [`tests/`](tests/) | Shared tooling and recipe-hook tests. |
| [`pgrx/`](pgrx/) | Rust installers, Cargo evidence, SBOM hook, templates and tests. |
