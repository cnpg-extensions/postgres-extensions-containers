# Upstream sync, 2026-11-24

Downstream `origin/main` at `f8a7cbca3f69140d0bacc683dcbbfab33a3b444a`. CloudNativePG `main` at `582dc0e4def3c227dbfe51062f90b1ff5bfbf6de`.
Previous recorded upstream tip and merge base: `019e7c20e8feb930a61e4799c108462c3b63485b`.

## Dependency updates

Retain the converged Dagger CLI and engine (0.21.12), CNPG (1.30.2),
Alpine (3.24, f59abe6), registry (3.1.2, 82f6ff4), login (8aa5831),
Bake (59cb120), Cosign installer (756fe2d), setup-go (d8cbb80) and
create-pull-request (3ffccac) pins. Retain kubectl 1.37.2 (06c6e02)
and the shared psql 18.7 test client (386eecb). Exclude all upstream
extension package, Dockerfile, README, fixture and library-list updates.

## Planned adoption

| Date | Commit | Subject | Exact mirror path present | Paths | Decision |
|---|---|---|---|---|---|
| 2026-11-02 | f1e7e53cc9f21460233afd5ac36b8535680807d4 | ci: exclude README.md from valid filter targets (#394) | Yes | .github/workflows/bake.yml | Already covered by downstream Markdown exclusions in both selectors. |
| 2026-11-20 | c7a1bc76dc30a674c3604ce0c276db2f76a2584c | fix(cosign): recursively sign promoted container images (#421) | Yes | .github/workflows/bake_targets.yml | Sign both assembled source indexes and Debian Bake outputs recursively. |
| 2026-11-23 | b12fd034b79ec27414b44c7bcf6b0bb29e35feea | feat: add PostgreSQL 19 builds for packaged extensions (#425) | Yes | Taskfile.yml, pg-crash/metadata.hcl, pg-ivm/metadata.hcl, pgaudit/metadata.hcl, pgvector/metadata.hcl, postgis/metadata.hcl, postgis/system-libs/19-bookworm-os-libs.txt, postgis/system-libs/19-trixie-os-libs.txt, wal2json/metadata.hcl | Adopt explicit PG major selection in the Taskfile. Exclude extension payloads. |

## Not relevant

| Date | Commit | Subject | Exact mirror path present | Paths | Decision |
|---|---|---|---|---|---|
| 2026-10-19 | 42e510a48317d1554c198391784b70c6318e8292 | chore: update postgis OS libraries (#372) | No | postgis/system-libs/18-bookworm-os-libs.txt, postgis/system-libs/18-trixie-os-libs.txt | Exclude upstream extension payloads and preserve downstream ownership. |
| 2026-11-12 | 988a118331b97fec87c41d7858d40cb68d12e203 | chore: update postgis OS libraries (#381) | No | postgis/system-libs/18-bookworm-os-libs.txt, postgis/system-libs/18-trixie-os-libs.txt | Exclude upstream extension payloads and preserve downstream ownership. |
| 2026-11-13 | 3f16bde11e56900322cf1bbd22899f68f6596781 | chore: update postgis OS libraries (#413) | No | postgis/system-libs/18-bookworm-os-libs.txt, postgis/system-libs/18-trixie-os-libs.txt | Exclude upstream extension payloads and preserve downstream ownership. |
| 2026-11-23 | 71c31861115fbb7505db41ca437d141015414ecb | feat: add pg19 builds for pgRouting (#426) | No | pgrouting/metadata.hcl | Exclude upstream extension payloads and preserve downstream ownership. |
| 2026-11-23 | 21143bf8852b12148be1fb225a3ea8534a16481c | chore: update postgis OS libraries (#422) | No | postgis/system-libs/18-trixie-os-libs.txt | Exclude upstream extension payloads and preserve downstream ownership. |

## Conflict resolution and downstream impact

Reviewed 52 commits since the October record, including 44 dependency chores.
Git paired upstream recipe changes with pg-stat-plans, timestamp9 and mobilitydb,
including new PG19 PostGIS library files. Restored all extension paths to the
downstream base and excluded resurrected upstream directories. The merge introduces
no extension, ownership, branding or registry-identity changes.

- Preserved the Debian change selector and its existing Markdown exclusions,
  representative samples, test-only triggers and PR authorization. The source
  selector applies the same exclusions after resolving PGRX and Universe paths.
- In both signing jobs, signed child manifests as well as their index using
  the existing immutable references. Preserved the source pipeline's Cosign
  compatibility flags. Both production jobs already call the shared copy-images
  action, which recursively signs the destination. Provenance stays index-scoped.
  Security, smoke and SLSA prerequisites and promotion conditions are unchanged.
- Kept the downstream shared CNPG support policy and its single latest pin.
  Preserved catalog composition, recipe discovery, registry cleanup and source
  build matrices. Upstream introduced no changes to these algorithms.
- Adapted the Taskfile selector across the three Bake families, which share the
  major/distro target suffix. Downstream recipes at this base declare PG18.
  Kept that default and allow PG_MAJOR overrides. Downstream main already includes #427, so the
  tested image's parsed major also selects the correct ClusterImageCatalog entry.
  This prevents testing a PG19 extension against a PG18 operand.
- Kept the downstream scheduling and checkout logic for OS-library updates.
  In the shared SQL test Job and Taskfile retained downstream configuration
  with the converged psql and kubectl pins from downstream #430 and #429.

## Validation

The following checks ran during initial preparation on downstream base
`8725f8715d250739dd16a4e56cc67c2b73b2883d`.

- Generated the ignored Dagger client with CLI 0.21.12 and restored the module
  declaration afterward. Maintenance Go tests passed. All 21 source-build
  discovery, assembly and contract tests in the top-level Python suite passed.
- Task parsed successfully. Executed the Taskfile jq command against Bake
  metadata from a real four-target registry build. PG18/trixie and
  PG19/bookworm each selected exactly the requested tag. PG20/trixie exited 4.
- Built an amd64/arm64 scratch index with BuildKit and pushed to an isolated
  local registry repository. Cosign 3.1.4 recursively signed it with a local
  key using the source pipeline compatibility flags. Verification by digest
  passed for the index and both child manifests.
- Dagger generated values from previously built PG18 and PG19 pgRouting images
  in the local registry using a temporary recipe fixture. Both emitted the
  correct numeric pg_major and kept PostGIS catalog-managed.
- Actionlint passed on the two edited workflows with ShellCheck disabled and
  its stale ubuntu-26.04 runner-label diagnostic excluded. git diff --check
  passed. No fresh native extension compilation, hosted keyless signing,
  production promotion or SLSA generation was exercised locally.
- Both PG18 and PG19 shared Chainsaw suites passed on the existing Kind cluster
  using the generated pgRouting values. Each provisioned its catalog-selected
  PostgreSQL operand and installed and verified the extension with its PostGIS
  dependency. The pinned SBOM-generator container passed all 45 contract tests.
- Ran the Taskfile's Buildx Bake check command in parallel for every recipe,
  with the appropriate source overlay. All 86 discovered Debian targets and
  all nine source recipes passed. These were BuildKit checks, not builds of
  extension binaries.
