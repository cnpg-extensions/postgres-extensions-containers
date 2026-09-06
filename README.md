[![CNPG Extensions](./logo/cnpg-extensions.png)](https://github.com/cnpg-extensions/)

# CNPG Extensions - PostgreSQL Extension Container Images

This repository provides **maintenance scripts** for building **immutable
container images** containing PostgreSQL extensions that cannot be accepted
into the upstream [cloudnative-pg/postgres-extensions-containers](https://github.com/cloudnative-pg/postgres-extensions-containers)
project due to licensing constraints, but are otherwise fully compatible with
[CloudNativePG](https://cloudnative-pg.io/).

## Documentation

- [Adding a New Extension](./CONTRIBUTING_NEW_EXTENSION.md): A step-by-step
  guide for contributors.
- [Building Locally](./BUILD.md): Technical instructions for the build system
  (Dagger/Task).
- [CloudNativePG Documentation](https://cloudnative-pg.io/documentation/current/imagevolume_extensions/):
  How to use these images in your cluster.

---

## Requirements

- **CloudNativePG** ≥ 1.27
- **PostgreSQL** ≥ 18 (requires the `extension_control_path` feature)
- **Kubernetes** 1.33+ (with [ImageVolume feature enabled in 1.33 and 1.34](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-image-volume-source/))

---

## Supported Extensions

| Extension | Description | Project URL | Maintained by | License blocker |
| :--- | :--- | :--- | :--- | :--- |
| **[age](age)** | Apache AGE graph database extension (Cypher queries) | [github.com/apache/age](https://github.com/apache/age) | @ardentperf | libcsv (LGPL-2.1+) |
| **[debversion](debversion)** | Debian package version comparison type | [salsa.debian.org/postgresql/postgresql-debversion](https://salsa.debian.org/postgresql/postgresql-debversion) | @ardentperf | GPL-3+ |
| **[h3](h3)** | Uber H3 hexagonal geospatial indexing | [github.com/zachasme/h3-pg](https://github.com/zachasme/h3-pg) | @ardentperf | libh3-1 (Apache-2.0 + AGPL-3+ test deps) |
| **[mobilitydb](mobilitydb)** | Spatio-temporal moving objects database | [mobilitydb.com](https://mobilitydb.com/) | @ardentperf | GPL-2+, GPL-3+ |
| **[mysql-fdw](mysql-fdw)** | MySQL/MariaDB foreign data wrapper | [github.com/EnterpriseDB/mysql_fdw](https://github.com/EnterpriseDB/mysql_fdw) | @ardentperf | libmariadb3 (LGPL-2.1) |
| **[pg-cron](pg-cron)** | Cron-based job scheduler for PostgreSQL | [github.com/citusdata/pg_cron](https://github.com/citusdata/pg_cron) | @ardentperf | Vixie-Cron (src/entry.c, src/misc.c) |
| **[pg-rrule](pg-rrule)** | iCalendar RRULE recurrence rule type | [github.com/petropavel13/pg_rrule](https://github.com/petropavel13/pg_rrule) | @ardentperf | libical3 (LGPL-2.1/MPL-2.0) |
| **[pg-uuidv7](pg-uuidv7)** | UUID version 7 (time-sortable) generator | [github.com/fboulnois/pg_uuidv7](https://github.com/fboulnois/pg_uuidv7) | @ardentperf | MPL-2.0 |
| **[pgagent](pgagent)** | PostgreSQL job scheduler (pgAdmin component) | [pgadmin.org](https://www.pgadmin.org/docs/pgadmin4/latest/pgagent.html) | @ardentperf | Boost libraries (BSL-1.0) |
| **[pgmemcache](pgmemcache)** | Memcached client interface for PostgreSQL | [github.com/ohmu/pgmemcache](https://github.com/ohmu/pgmemcache) | @ardentperf | libmemcached11 (LGPL) |
| **[pgmp](pgmp)** | GMP arbitrary-precision arithmetic types | [github.com/dvarrazzo/pgmp](https://github.com/dvarrazzo/pgmp) | @ardentperf | LGPL-3+ |
| **[pgsphere](pgsphere)** | Spherical geometry for astronomical data | [pgsphere.github.io](https://pgsphere.github.io/) | @ardentperf | GPL-3+ |
| **[pldebugger](pldebugger)** | PL/pgSQL interactive debugger (pldbgapi) | [github.com/EnterpriseDB/pldebugger](https://github.com/EnterpriseDB/pldebugger) | @ardentperf | Artistic-2.0 |
| **[plprofiler](plprofiler)** | PL/pgSQL execution profiler | [github.com/bigsql/plprofiler](https://github.com/bigsql/plprofiler) | @ardentperf | Artistic-2.0 |
| **[plr](plr)** | R procedural language for PostgreSQL | [joeconway.com/plr](https://www.joeconway.com/plr/) | @ardentperf | GPL-2+ |
| **[q3c](q3c)** | Quad Tree Cube sky survey spatial indexing | [github.com/segasai/q3c](https://github.com/segasai/q3c) | @ardentperf | GPL-2+ |
| **[snakeoil](snakeoil)** | ClamAV antivirus scanning for PostgreSQL | [github.com/credativ/pg_snakeoil](https://github.com/credativ/pg_snakeoil) | @ardentperf | libclamav12 (LGPL-2+) |
| **[tds-fdw](tds-fdw)** | Microsoft SQL Server / Sybase foreign data wrapper | [github.com/tds-fdw/tds_fdw](https://github.com/tds-fdw/tds_fdw) | @ardentperf | libsybdb5/FreeTDS (LGPL-2+) |

Extensions in this repository are not accepted upstream solely due to licensing
— they are otherwise fully functional and meet all other upstream quality
requirements.

---

## Relationship to Upstream

This repository tracks the upstream
[cloudnative-pg/postgres-extensions-containers](https://github.com/cloudnative-pg/postgres-extensions-containers)
build infrastructure as closely as possible. The only intentional differences are:

- Extensions present upstream are removed here (they are maintained there).
- Extensions blocked upstream by licensing are added here.

This keeps merging upstream infrastructure improvements straightforward.

---

## Contribution and Maintenance Policy

Contributors are welcome to propose and maintain additional extensions.

### Governance and Compliance

The project adheres to the following frameworks:

- **Governance Model:** complies with the CloudNativePG (CNPG) Governance
  Model, as defined in [`GOVERNANCE.md`](GOVERNANCE.md).
- **Code of Conduct:** follows the CNCF Code of Conduct, as defined in
  [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

### Extension Requirements

When proposing a new extension, the following criteria must be met:

- **Licensing:** The extension must have been declined by the upstream
  cloudnative-pg project solely due to a license not on the
  [CNCF Allowlist](https://github.com/cncf/foundation/blob/main/policies-guidance/allowed-third-party-license-policy.md).
  All other upstream quality requirements still apply.
- **Structure:** only one extension can be included within an extension folder.
- **Debian Packages:** Extension images must be built **exclusively** from
  Debian packages in the `main` component (which by definition complies with
  the [DFSG](https://www.debian.org/social_contract#guidelines)), sourced from
  a trusted, auditable repository.
  The [PostgreSQL Global Development Group (PGDG)](https://wiki.postgresql.org/wiki/Apt)
  is the recommended source, but other Debian repositories are acceptable
  provided they meet the same standards.
- **License inclusion:** all necessary license agreements for the extension and
  its dependencies must be included within the extension folder.

See [Adding a New Extension](./CONTRIBUTING_NEW_EXTENSION.md) for the full
workflow on proposing and submitting a new extension.

### Automated Dependency Updates

CNPG Extensions enables Renovate automerge by default for extension dependency
updates. This policy assumes that upstream versions follow semantic versioning:
minor and patch updates may be automerged after the required checks pass, but
major version changes are not automerged and require manual review.

If minor updates should not be automerged for a particular extension, an
extension-specific rule can disable automerge in [`renovate.json`](renovate.json).
[`mysql-fdw`](mysql-fdw) is an example; its package updates are configured for
manual review.

### Submission Process

1. **Request and commitment:** Open a new issue requesting the extension.
   The contributor(s) must agree to become "component owners" and maintainers
   for that extension.
2. **Approval:** Maintainers review the proposal and either approve it or
   request changes.
3. **Submission:** Component owner(s) open a Pull Request (PR) to introduce
   the new extension. The PR must include an entry in the `CODEOWNERS` file
   adding the component owner(s) for the new extension folder. The PR is
   reviewed, approved, and merged.
4. **Naming:** The name of the extension is the registry name.

### Removal Policy

If component owners decide to stop maintaining their extension, and no other
contributors are found, the main project maintainers reserve the right to
**unconditionally remove that extension**.

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

### SBOM scope

> [!WARNING]
> The published SBOM and all SBOM/provenance annotations are a beta,
> provisional implementation. They are not a complete or final OpenSSF
> compliance claim. Their schema and fields may change or be removed as the
> project moves toward stronger and more complete OpenSSF compliance. A
> signature binds the exact bytes produced, but does not make provisional
> contents or fields stable.

Our goal is for this provisional data to be useful in the interim for license
inventory and consumption by security scanners, while industry standards and
industry build toolchains continue to mature in this space.

The published SBOM is composed from the SPDX predicate produced for the
post-install `builder` stage and the final-image file subjects in that
attestation. It contains packages that own files shipped in the final image,
plus an extension-specific artifacts package for files without a package owner.
The file list is limited to files actually shipped in the image, including
copied system libraries and license files. Relationships are trimmed and
rewritten to match the resulting package and file lists.
The workflow adds the provisional composition manifest as a canonical,
document-level SPDX `OTHER` annotation after `compose_sbom.py` produces the
aggregate; the composer itself remains focused on SBOM inventory composition.

The final scratch stage is not scanned or read as an SBOM. During CI, the
builder SBOM and its final-image file subjects are composed into one SPDX
predicate per image target, aggregating the platform-specific results. The
single aggregate is signed by GitHub Actions and attached to the
multi-platform image index. This keeps the SBOM focused on the extension
payload while still making vulnerabilities in shipped system-library and
PostgreSQL packages visible. BuildKit's image provenance remains a separate
attestation because it describes how the image was built rather than what the
image contains.

## Container authenticity and provenance

The workflow follows the verification pattern described in CloudNativePG's
[security documentation](https://cloudnative-pg.io/docs/devel/security/),
adapted for this repository's separate BuildKit and GitHub Actions
attestations.

The commands below use an immutable multi-platform image index. Replace
`<IMAGE>` with the full image name without a tag, such as
`ghcr.io/cnpg-extensions/plr`, and replace `<INDEX_DIGEST>` with the index
digest (`sha256:...`). Prefer a digest over a tag when verifying or retrieving
security metadata.

### Verify image authenticity

Images are signed using keyless Cosign signatures issued through GitHub's
OIDC identity. For a production image built from `main`, verify the signature
and the signing workflow with:

```bash
cosign verify "<IMAGE>@<INDEX_DIGEST>" \
  --certificate-identity-regexp='^https://github.com/cnpg-extensions/postgres-extensions-containers/.github/workflows/bake_targets\.yml@refs/heads/main$' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com'
```

The workflow identity is the reusable `bake_targets.yml` workflow. Images
created from another branch have a corresponding branch-scoped identity and
should be verified with that ref instead.

### Retrieve and verify the aggregate SBOM attestation

The aggregate SBOM is a GitHub Actions artifact attestation attached to the
multi-platform index. This is one SBOM attestation for the whole index, rather
than one SBOM attestation per platform. `gh attestation verify` verifies the
signed in-toto statement and can also extract its SPDX predicate:

```bash
gh attestation verify "oci://<IMAGE>@<INDEX_DIGEST>" \
  --repo cnpg-extensions/postgres-extensions-containers \
  --predicate-type https://spdx.dev/Document/v2.3 \
  --format json \
  --jq '.[].verificationResult.statement.predicate' > image-sbom.spdx.json
```

To retain the complete signed statement, including the SPDX composition
annotation and its verification metadata, extract the statement instead:

```bash
gh attestation verify "oci://<IMAGE>@<INDEX_DIGEST>" \
  --repo cnpg-extensions/postgres-extensions-containers \
  --predicate-type https://spdx.dev/Document/v2.3 \
  --format json \
  --jq '.[].verificationResult.statement' > image-sbom.attestation.json
```

The annotation records the builder SBOM hash for each platform, the build
definition hash, source and image digests, composer/tool details, and the
GitHub workflow/run identity. It is intentionally provisional along with the
rest of this SBOM implementation; consumers should not treat its field set as
a stable API. `gh attestation verify` verifies the attestation's signer,
subject digest, and predicate type; consumers that rely on the composition
details should additionally inspect the annotation contents.

The extracted SPDX JSON can be processed by standard SBOM tooling. For
example, scan it with Trivy for vulnerabilities and license findings:

```bash
trivy sbom --scanners vuln,license image-sbom.spdx.json
```

### Retrieve and verify BuildKit image provenance

BuildKit's SLSA image provenance is kept as a separate, per-platform image
attestation. Retrieve a platform's provenance with `buildx`:

```bash
docker buildx imagetools inspect "<IMAGE>@<INDEX_DIGEST>" \
  --format '{{ json (index .Provenance "linux/amd64").SLSA }}' \
  > buildkit-provenance-linux-amd64.json

docker buildx imagetools inspect "<IMAGE>@<INDEX_DIGEST>" \
  --format '{{ json (index .Provenance "linux/arm64").SLSA }}' \
  > buildkit-provenance-linux-arm64.json
```

Where supported by the installed verifier, verify the BuildKit SLSA
provenance against this repository's source URI:

```bash
slsa-verifier verify-image \
  "<IMAGE>@<INDEX_DIGEST>" \
  --source-uri github.com/cnpg-extensions/postgres-extensions-containers
```

This verifies the BuildKit provenance separately from the signed GitHub SBOM
attestation. The two artifacts intentionally answer different questions: the
BuildKit attestation describes the build, while the GitHub SBOM attestation
binds the composed inventory and its composition evidence to the image index.

## Image catalogs

To simplify the deployment of PostgreSQL extensions, this project automatically
generates `ClusterImageCatalog` resources. These catalogs provide a curated
list of compatible extension images for PostgreSQL 18+ versions. The generated
catalog starts from CNPG's [upstream extension catalog](https://github.com/cloudnative-pg/artifacts/tree/main/image-catalogs-extensions),
then adds the images maintained in this repository. Definitions from the
upstream catalog are retained.

- **Frequency:** Built once a week.
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
