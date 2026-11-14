# Shared source builds

The [canonical design and acceptance evidence](https://github.com/ardentperf-labs/postgres-extensions-containers/issues/3)
tracks this implementation. Recipes live in `pgrx/<name>` and `universe/<name>`;
this directory contains only shared infrastructure. Location determines the
family. The legacy PGRX `build_system` field is ignored.

`source-build.yml` selects recipes and reports one `Source-build acceptance`
check. `source-build-targets.yml` preserves native preparation, separate platform
builds, complete index assembly, signing, security, shared CNPG smoke tests,
testing provenance, trusted-main promotion, and production provenance. Catalog
refresh uses the existing repository dispatch and catalog-generation flow.

## Local acceptance

Use a local registry to preserve BuildKit SPDX and provenance attestations.
Create a Docker-container Buildx builder, then run `build.py --architecture
amd64 --builder NAME` (or `arm64` on ARM). Host, daemon and worker must agree.
Preparation accepts JSON containing `extension_name` and `build_family`:

```sh
GITHUB_REPOSITORY_OWNER=ardentperf-labs GITHUB_RUN_ID=local registry=localhost:5000 \
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

CI retains the pre-migration PGRX security checks: the shared upstream
`security-scans` action runs Dockle and optional Snyk. Universe adds no Grype or
Grant CI step. The shared generator's inventory, notices and SPDX validation
remain part of building the images. For optional local vulnerability and license
reports, use the existing [consumer verification guide](../pgrx/README.md#verify-images).
The CNPG smoke matrix is unchanged from PGRX; image builds still use native
AMD64 and ARM64 runners.

## PR execution and rollout

Preserve PR295's existing authorization model. Fork PR tests use the trusted base
`maintainer-pr-tests.yml` workflow, which accepts repository Write, Maintain or
Admin permission. Same-repository PRs and manual dispatches retain the existing
entrypoints. The source workflow is renamed for both source-build families;
there is no additional per-job authorization layer.

Repository maintainers maintain all extensions. Renovate's existing root
configuration determines which updates qualify for automerge, subject to
Debian's `Automerge gate` and the shared `Source-build acceptance` gate.

Catalog generation retains the existing image lookup, upstream precedence,
runtime settings, and publication workflow. There is no separate accepted-release
inventory, source-SHA dispatch payload, or candidate-catalog acceptance path.

Historical PGRX signature verification remains documented in `pgrx/README.md`.
The renamed hosted signing and SLSA identities require separate hosted validation;
local checks do not establish those outcomes. Keep implementation build validation
limited to pg-duckdb, pg-durable and debversion. See the canonical issue for dated
validation evidence; earlier results do not validate subsequent changes.
