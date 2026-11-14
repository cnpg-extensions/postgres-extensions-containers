# Shared source builds

The [canonical design and acceptance evidence](https://github.com/ardentperf-labs/postgres-extensions-containers/issues/3)
tracks this implementation. Recipes live in `pgrx/<name>` and `universe/<name>`;
this directory contains only shared infrastructure. Location determines the
family. The legacy PGRX `build_system` field is ignored.

`source-build.yml` selects recipes and reports one `Source-build acceptance`
check. `source-build-targets.yml` preserves native preparation, separate platform
builds, complete index assembly, signing, security, shared CNPG smoke tests,
testing provenance, trusted-main promotion, and production provenance. Catalog
handoff follows the full gate. An unpublished metadata version cannot replace
the previous accepted source digest.

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
and the candidate digest. Generated values include the actual candidate catalog;
the Cluster requests the extension by name. Shared installation/version checks
and the pod's candidate image-volume digest assertion always run. Existing
recipe suites also run when present; Universe requires no separate suite.

CI retains the pre-migration PGRX security checks: the shared upstream
`security-scans` action runs Dockle and optional Snyk. Universe adds no Grype or
Grant CI step. The shared generator's inventory, notices and SPDX validation
remain part of building the images. For optional local vulnerability and license
reports, use the existing [consumer verification guide](../pgrx/README.md#verify-images).
The CNPG smoke matrix is unchanged from PGRX; image builds still use native
AMD64 and ARM64 runners.

## Privileged execution and rollout

PR execution enters through the trusted base `maintainer-pr-tests.yml` workflow
for both fork and same-repository PRs. Repository Admin permission is required;
Write/Maintain access does not authorize execution. Reruns
validate the triggering admin and reject a changed head SHA. Each candidate
preparation, platform build, assembly, and security job repeats the inline check
before checkout, including when only that failed job is rerun. The Debian build
and security jobs do the same; a successful upstream authorization job is not
authorization for a later rerun. Read-only smoke/tooling jobs receive no publishing
or signing credentials. Manual execution
uses the protected main selector and an explicit PR number for branch testing.

Repository maintainers maintain all extensions. Renovate's existing root
configuration determines which updates qualify for automerge, subject to the
required build/test checks. Keep Debian's `Automerge gate` and the shared
`Source-build acceptance` gate; this does not require a separate bot-diff policy
check or an extension-owner review-exemption mechanism. Privileged execution
continues to use the existing admin authorization checks described above.

Historical PGRX signature verification remains documented in `pgrx/README.md`.
The renamed hosted signing and SLSA identities must be observed and verified
before publishing updated consumer verification commands. Local acceptance does
not establish hosted identity, ARM64 runtime, protection, or Renovate auto-merge.

For bounded candidate validation, dispatch the protected main selector with
`pr_number`, its exact `expected_sha`, one `extension_name`, and
`validation_only=true`. This runs the normal target pipeline without production
promotion and reports `Scoped Source-build acceptance` or `Scoped Automerge gate`.
These statuses do not replace the full required PR gates. The initial migration
uses only `pg-duckdb`, `pg-durable`, and `debversion` for build acceptance; the
remaining moved recipes receive the required baseline audit and static checks.
