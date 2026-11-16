[![CNPG Extensions](./logo/cnpg-extensions.png)](https://github.com/cnpg-extensions/)

# CNPG Extensions - PostgreSQL Extension Container Images

This repository provides **maintenance scripts** for building **immutable
container images** containing Debian-packaged and source-built PostgreSQL
extensions for [CloudNativePG](https://cloudnative-pg.io/).

## Documentation

- [Adding a New Extension](./CONTRIBUTING_NEW_EXTENSION.md): A step-by-step
  guide for contributors.
- [Building Locally](./BUILD.md): Technical instructions for the build system
  (Dagger/Task).
- [Upstream Workarounds](./WORKAROUNDS.md): Temporary measures and the upstream
  fixes needed to retire them.
- [CloudNativePG Documentation](https://cloudnative-pg.io/documentation/current/imagevolume_extensions/):
  How to use these images in your cluster.

---

## Requirements

- **CloudNativePG** ≥ 1.27
- **PostgreSQL** ≥ 18 (requires the `extension_control_path` feature)
- **Kubernetes** 1.33+ (with [ImageVolume feature enabled in 1.33 and 1.34](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-image-volume-source/))

---

## Supported Extensions

The [upstream CloudNativePG catalog](https://github.com/cloudnative-pg/artifacts/tree/main/image-catalogs-extensions)
is automatically included in this project's image catalogs. For the same
extension, distribution and PostgreSQL major version, the upstream entry always
takes precedence over an entry maintained here.

**Upstream CloudNativePG extensions:** [pg-crash](https://github.com/cloudnative-pg/postgres-extensions-containers/tree/main/pg-crash), [pg-ivm](https://github.com/cloudnative-pg/postgres-extensions-containers/tree/main/pg-ivm), [pgaudit](https://github.com/cloudnative-pg/postgres-extensions-containers/tree/main/pgaudit), [pgrouting](https://github.com/cloudnative-pg/postgres-extensions-containers/tree/main/pgrouting), [pgvector](https://github.com/cloudnative-pg/postgres-extensions-containers/tree/main/pgvector), [postgis](https://github.com/cloudnative-pg/postgres-extensions-containers/tree/main/postgis), [timescaledb-oss](https://github.com/cloudnative-pg/postgres-extensions-containers/tree/main/timescaledb-oss), [wal2json](https://github.com/cloudnative-pg/postgres-extensions-containers/tree/main/wal2json).

For this grouping, CNCF-compatible means covered by Apache-2.0 or the
[CNCF license allowlist](https://github.com/cncf/foundation/blob/main/policies-guidance/allowed-third-party-license-policy.md)
without project-specific exceptions. Packages with non-allowlisted terms or
unresolved dependency or attribution questions are outside the compatible group.
Consult each recipe and image's notices and SBOM for license details.

**Debian packages with CNCF-compatible declared licenses:** [credcheck](credcheck), [db2fce](db2fce), [decoderbufs](decoderbufs), [extra-window-functions](extra-window-functions), [first-last-agg](first-last-agg), [hll](hll), [http](http), [hypopg](hypopg), [ip4r](ip4r), [jsquery](jsquery), [mimeo](mimeo), [periods](periods), [pg-background](pg-background), [pg-csv](pg-csv), [pg-dirtyread](pg-dirtyread), [pg-partman](pg-partman), [pg-permissions](pg-permissions), [pg-qualstats](pg-qualstats), [pg-rage-terminator](pg-rage-terminator), [pg-repack](pg-repack), [pg-rewrite](pg-rewrite), [pg-similarity](pg-similarity), [pg-squeeze](pg-squeeze), [pg-stat-kcache](pg-stat-kcache), [pg-stat-log](pg-stat-log), [pg-statviz](pg-statviz), [pg-track-settings](pg-track-settings), [pg-wait-sampling](pg-wait-sampling), [pgextwlist](pgextwlist), [pgfincore](pgfincore), [pglogical](pglogical), [pgnodemx](pgnodemx), [pgpcre](pgpcre), [pgq](pgq), [pgsentinel](pgsentinel), [pgtap](pgtap), [pgtt](pgtt), [pllua](pllua), [plpgsql-check](plpgsql-check), [plproxy](plproxy), [plsh](plsh), [pointcloud](pointcloud), [powa](powa), [preprepare](preprepare), [prioritize](prioritize), [rational](rational), [roaringbitmap](roaringbitmap), [rum](rum), [semver](semver), [set-user](set-user), [tdigest](tdigest), [timestamp9](timestamp9), [toastinfo](toastinfo).

**Debian packages outside the CNCF-compatible group:** [age](age), [asn1oid](asn1oid), [debversion](debversion), [h3](h3), [icu-ext](icu-ext), [mobilitydb](mobilitydb), [mysql-fdw](mysql-fdw), [numeral](numeral), [ogr-fdw](ogr-fdw), [orafce](orafce), [pg-cron](pg-cron), [pg-gvm](pg-gvm), [pg-hint-plan](pg-hint-plan), [pg-pwhash](pg-pwhash), [pg-rrule](pg-rrule), [pg-stat-plans](pg-stat-plans), [pg-uuidv7](pg-uuidv7), [pgmemcache](pgmemcache), [pgmp](pgmp), [pgsphere](pgsphere), [pldebugger](pldebugger), [pljs](pljs), [plprofiler](plprofiler), [pltcl](pltcl), [prefix](prefix), [q3c](q3c), [rdkit](rdkit), [show-plans](show-plans), [table-log](table-log), [tds-fdw](tds-fdw), [unit](unit).

**Source-built PGRX packages:** [pg-durable](pgrx/pg-durable), [pg-graphql](pgrx/pg-graphql), [pg-jsonschema](pgrx/pg-jsonschema), [pg-parquet](pgrx/pg-parquet), [pg-search](pgrx/pg-search), [pg-session-jwt](pgrx/pg-session-jwt), [pglinter](pgrx/pglinter), [postgresql-anonymizer](pgrx/postgresql-anonymizer).

**Source-built Universe packages:** [pg-duckdb](universe/pg-duckdb).

Published extensions are available in both the [Trixie](https://github.com/cnpg-extensions/artifacts/blob/main/image-catalogs-extensions/catalog-minimal-trixie.yaml)
and [Bookworm](https://github.com/cnpg-extensions/artifacts/blob/main/image-catalogs-extensions/catalog-minimal-bookworm.yaml)
catalogs, except `pg-gvm` and `rdkit`, which are Trixie-only.

---

## Relationship to Upstream

This repository tracks the upstream
[cloudnative-pg/postgres-extensions-containers](https://github.com/cloudnative-pg/postgres-extensions-containers)
build infrastructure as closely as possible. Recipe organization differs as follows:

- Extensions present upstream are removed here (they are maintained there).
- Additional extensions use Debian packages or the PGRX and Universe source-build paths.

This keeps merging upstream infrastructure improvements straightforward.

---

## Contribution and Maintenance Policy

Contributors are welcome to propose additional extensions. Repository maintainers
maintain all extensions.

### Governance and Compliance

The project adheres to the following frameworks:

- **Governance Model:** complies with the CloudNativePG (CNPG) Governance
  Model, as defined in [`GOVERNANCE.md`](GOVERNANCE.md).
- **Code of Conduct:** follows the CNCF Code of Conduct, as defined in
  [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

### Extension Requirements

When proposing a new extension, the following criteria must be met:

- **Licensing:** All distributed components must comply with the
  [Open Source Licensing Policy](source-build/README.md#open-source-licensing-policy).
- **Structure:** only one extension can be included within an extension folder.
- **Debian Packages:** Prefer extensions available as Debian packages in the `main` component (which by definition complies with
  the [DFSG](https://www.debian.org/social_contract#guidelines)), sourced from
  a trusted, auditable repository. Extensions added through the Debian framework
  should have packages available for both current Debian `stable` and `oldstable`.
  The [PostgreSQL Global Development Group (PGDG)](https://wiki.postgresql.org/wiki/Apt)
  is the recommended source, but other Debian repositories are acceptable
  provided they meet the same standards. Rust extensions use the [PGRX path](pgrx/README.md);
  other source builds must meet the [Source Build inclusion criteria](source-build/README.md#inclusion-policy-debian-packaging-first).
- **Dependency evidence:** Identify shipped dependencies and their actual versions,
  preserve required notices, and account for them in the shared SBOM. Source builds
  must meet the [dependency evidence requirements](source-build/README.md#dependency-evidence-in-the-sbom)
  and use the existing build and release infrastructure.
- **License inclusion:** all necessary license agreements for the extension and
  its dependencies must be included within the extension folder.

See [Adding a New Extension](./CONTRIBUTING_NEW_EXTENSION.md) for the full
workflow on proposing and submitting a new extension.

### Automated Dependency Updates

Renovate automatically merges eligible minor, patch, and digest updates once
required checks pass. Major updates and packages without a verified SQL version
mapping require manual review. Packages containing independently versioned SQL
extensions also require manual review. The Automerge gate checks extension
updates for prerelease version markers, with an exception for AGE's release
naming.

### Submission Process

1. **Proposal and discussion:** Open a GitHub issue to suggest an extension or
   discuss its packaging and licensing requirements. Pull requests are welcome
   but are not required to propose an extension or participate in discussion.
2. **Review:** Repository maintainers review proposals and work with contributors
   on requirements and implementation. Maintainers maintain all extensions.
3. **Naming:** The name of the extension is the registry name.

---

## Naming & Tagging Convention

Each extension image tag follows this format:

```
<extension-name>:<ext_version>-<timestamp>-<pg_version>-<distro>
```

**Example:**
Building `pg_cron` version `1.6.7` on PostgreSQL `18.0` for the `trixie`
distro, with build timestamp `202509101200`, results in:

```
pg-cron:1.6.7-202509101200-18-trixie
```

For convenience, **rolling tags** should also be published:

```
pg-cron:1.6.7-18-trixie
```

This scheme ensures:

- Alignment with the upstream `postgres-containers` base images
- Explicit PostgreSQL and extension versioning
- Multi-distro support

---

## Image Labels

Each extension image includes OCI-compliant labels for runtime inspection
and tooling integration. These metadata fields enable CloudNativePG and
other tools to identify the base PostgreSQL version and OS distribution.

### CloudNativePG-Specific Labels

| Label                                 | Description                      | Example                                                 |
|:--------------------------------------|:---------------------------------|:--------------------------------------------------------|
| `io.cloudnativepg.image.base.name`    | Base PostgreSQL container image  | `ghcr.io/cloudnative-pg/postgresql:18-minimal-bookworm` |
| `io.cloudnativepg.image.base.pgmajor` | PostgreSQL major version         | `18`                                                    |
| `io.cloudnativepg.image.base.os`      | Operating system distribution    | `bookworm`                                              |
| `io.cloudnativepg.image.sql.version`  | PostgreSQL extension SQL version | `1.6`                                                   |

### Standard OCI Labels

In addition to CloudNativePG-specific labels, all images include standard OCI
annotations as defined by the [OCI Image Format Specification](https://github.com/opencontainers/image-spec/blob/main/annotations.md):

| Label                                  | Description                 |
|:---------------------------------------|:----------------------------|
| `org.opencontainers.image.created`     | Image creation timestamp    |
| `org.opencontainers.image.version`     | Extension's package version |
| `org.opencontainers.image.revision`    | Git commit SHA              |
| `org.opencontainers.image.title`       | Human-readable image title  |
| `org.opencontainers.image.description` | Image description           |
| `org.opencontainers.image.source`      | Source repository URL       |
| `org.opencontainers.image.licenses`    | License identifier          |

You can inspect these labels using container tools:

```bash
# Using docker buildx imagetools
docker buildx imagetools inspect <image> --raw | jq '.annotations'

# Using skopeo
skopeo inspect docker://<image> | jq '.Labels'
```

## SBOMs and authenticity

Use the [SBOM guide](https://github.com/cnpg-extensions/cnpg-sbom-generator) to verify an extension image,
extract its platform-specific SPDX, and report vulnerabilities and licenses with
Grype and Grant. See the [example report](./examples/sbom-reports.txt) and
[generator release workflow](https://github.com/cnpg-extensions/cnpg-sbom-generator/blob/main/.github/workflows/sbom-generator.yml).

### Verify images

Follow the SBOM guide to [verify the image and extract its
SBOM](https://github.com/cnpg-extensions/cnpg-sbom-generator#verify-the-image-and-extract-its-sbom),
[inspect and verify build provenance](https://github.com/cnpg-extensions/cnpg-sbom-generator#inspect-and-verify-build-provenance),
and [report vulnerabilities and licenses](https://github.com/cnpg-extensions/cnpg-sbom-generator#report-vulnerabilities-and-licenses).
The tools listed in that guide are sufficient; no build toolchain is needed.

Debian, PGRX and Universe images use the same verification tools and published
SBOM format. For images published by `cnpg-extensions` from `main`, choose the
exact `--certificate-identity` for the workflow that published the image.

For Debian images:

```text
https://github.com/cnpg-extensions/postgres-extensions-containers/.github/workflows/bake_targets.yml@refs/heads/main
```

For PGRX and Universe images published through the shared source workflow:

```text
https://github.com/cnpg-extensions/postgres-extensions-containers/.github/workflows/source-build-targets.yml@refs/heads/main
```

Keep the guide's GitHub Actions OIDC issuer and add
`--new-bundle-format=false` for this repository's legacy-format signatures.
For another publisher, change both the image repository and the exact workflow
identity to that publisher's repository and trusted branch. After copying an
image, verify the destination repository's signature as well.

The guide's extraction examples use a multi-platform index. For a
single-platform index, confirm its platform with `docker buildx imagetools
inspect`, then use `.SBOM.SPDX` and `.Provenance.SLSA` in the format expressions.

Scan the PostgreSQL base image separately using its own SBOM.

## Image catalogs

To simplify the deployment of PostgreSQL extensions, this project automatically
generates `ClusterImageCatalog` resources. These catalogs provide a curated
list of compatible extension images for PostgreSQL 18+ versions. The generated
catalog starts from CNPG's [upstream extension catalog](https://github.com/cloudnative-pg/artifacts/tree/main/image-catalogs-extensions),
then adds the images maintained in this repository. Definitions from the
upstream catalog are retained.

- **Frequency:** Refreshed daily at 10:00 UTC and after successful extension
  builds on `main`, including builds triggered by extension or dependency updates.
  Every refresh pulls the latest upstream catalog from `main`, so upstream
  additions can appear here much sooner than 24 hours whenever an extension
  rebuild completes. Otherwise, the daily refresh normally picks them up within
  24 hours; delayed or failed workflow runs can extend this interval. To refresh
  sooner, manually run the
  [Update Extension Image Catalogs workflow](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/workflows/update-catalogs.yml)
  on `main`.
- **Location:** Published in the [`artifacts`
  repository](https://github.com/cnpg-extensions/artifacts/tree/main/image-catalogs-extensions).
- **Naming Convention:** These are based on the `minimal` catalog and use the
  `catalog-minimal` prefix (e.g., `catalog-minimal-trixie.yaml`)

For example, apply the PostgreSQL 18 catalog for Debian trixie with:

```bash
kubectl apply -f \
  https://raw.githubusercontent.com/cnpg-extensions/artifacts/main/image-catalogs-extensions/catalog-minimal-trixie.yaml
```

Clusters using this catalog should reference it instead of the corresponding
upstream base catalog; it already includes the upstream extension definitions.

PGRX and Universe build contributors: see the [shared build and local validation guide](./source-build/README.md).
