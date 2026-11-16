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

- **CloudNativePG** ≥ 1.29 (extension image catalog support)
- **PostgreSQL** ≥ 18 (requires the `extension_control_path` feature)
- **Kubernetes** 1.33+ (enable ImageVolume explicitly on 1.33 and 1.34; enabled by default on 1.35+)
- **Container runtime** with ImageVolume support: containerd 2.1+ or CRI-O 1.31+

See the [CNPG requirements](https://cloudnative-pg.io/docs/1.30/imagevolume_extensions/#requirements).

---

<a id="image-catalogs"></a>

## Quick start

Use the CNPG Extensions image catalog, **extension-update email alerts**, and a
**weekly catalog-update CronJob** as the standard installation and maintenance
path. The catalog includes upstream CloudNativePG extensions as well as the
Debian, PGRX, and Universe extensions maintained here. Upstream entries always
take precedence for the same extension, distribution, and PostgreSQL major.

### 1. Install the catalog and choose your extensions

Apply the Trixie catalog once:

```sh
kubectl apply -f https://raw.githubusercontent.com/cnpg-extensions/artifacts/main/image-catalogs-extensions/catalog-minimal-trixie.yaml
```

This is a drop-in replacement for the corresponding upstream
`postgresql-minimal-trixie` catalog, with additional extensions. For Bookworm,
use `catalog-minimal-bookworm.yaml` and `postgresql-minimal-bookworm` instead.
Choose the distribution used by your cluster; changing distributions is a
separate migration. See the [published catalogs](https://github.com/cnpg-extensions/artifacts/tree/main/image-catalogs-extensions)
and [CloudNativePG installation and usage documentation](https://cloudnative-pg.io/docs/1.30/image_catalog/#installation-and-usage).

Reference the catalog and select extensions by name. For example, this installs
PL/Tcl in the default `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: example
spec:
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    extensions:
      - name: pltcl
---
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: example-app
spec:
  name: app
  owner: app
  cluster:
    name: example
  extensions:
    - name: pltcl
```

The catalog supplies immutable image references and any required
`ld_library_path` and `env` values. You do not need to copy those settings into
your Cluster. A `Database` extension entry without `version` installs the
available default version initially. The catalog extension name and SQL extension
name can differ: each [extension README](#supported-extensions) gives both.

Keep required `shared_preload_libraries`, PostgreSQL parameters, and dependent
extensions in your manifests as shown in those READMEs; the catalog does not
add them automatically. Installing the catalog alone does not enable every
extension. See [CNPG's extension configuration](https://cloudnative-pg.io/docs/1.30/imagevolume_extensions/#configuration-source-and-precedence).

### 2. Set up extension-update monitoring and email first

**Create and verify monitoring before installing the CronJob below.** Image
updates can leave SQL extension upgrades pending in individual databases.
An email alert makes that follow-up work visible after weekly maintenance.

With [CNPG metrics being scraped by Prometheus](https://cloudnative-pg.io/docs/1.30/monitoring/),
use this query:

```promql
max by (namespace, cluster, datname, extname, installed_version, default_version) (
  cnpg_pg_extensions_update_available
) == 1
```

It returns installed extensions whose SQL version differs from the default
available in the running PostgreSQL instance, with both versions included in
the labels. It does not check the registry for newer images or report extensions
that have not been created in a database. The aggregation removes duplicate
replica results. Ensure your scrape configuration provides `namespace` and
`cluster` labels; adapt the grouping to your actual cluster identity labels,
including the Kubernetes cluster identifier when monitoring several clusters.

Use it in one of these three ways:

- **Grafana alert with email:** create an alert rule for returned values above
  zero and route it to an [email contact point](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/configure-email/).
  Configure SMTP for self-hosted Grafana and send a test notification.
- **Prometheus alert with Alertmanager email:** use the query as an alert rule's
  `expr` and route firing alerts to an [Alertmanager email receiver](https://prometheus.io/docs/alerting/latest/configuration/#email_config).
- **Grafana dashboard:** use an instant table query to display cluster, database,
  extension, installed version, and available default version. Pair the dashboard
  with an email alert for unattended maintenance.

First confirm the unfiltered `cnpg_pg_extensions_update_available` metric is
being collected. No results from the filtered query can mean everything is up
to date, but can also mean the metric is missing. Keep scrape failures and
CronJob failures covered by your usual monitoring. See the
[CNPG metric definition](https://github.com/cloudnative-pg/charts/blob/main/charts/cloudnative-pg/values.yaml).

### 3. Schedule your weekly maintenance

Once monitoring and email delivery work, install this CronJob. It refreshes the
catalog **every Tuesday at 1 AM Eastern**, adjusting for daylight saving time.
CNPG then rolls out changed PostgreSQL and selected extension images to clusters
referencing that catalog, keeping the selected PostgreSQL major version.

The schedule defines the start of your weekly maintenance window. It does not
impose an end time on rollouts or prevent changes initiated by other controllers
or administrators. Apply this example in the `default` namespace after creating
the ServiceAccount and permissions shown below.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: update-catalog
spec:
  schedule: "0 1 * * 2"
  timeZone: America/New_York
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: catalog-updater
          restartPolicy: OnFailure
          containers:
            - name: kubectl
              image: alpine/kubectl:latest
              command: ["kubectl", "apply", "-f"]
              args:
                - https://raw.githubusercontent.com/cnpg-extensions/artifacts/main/image-catalogs-extensions/catalog-minimal-trixie.yaml
```

<details>
<summary>ServiceAccount and RBAC: apply before the CronJob</summary>

The catalog must already exist from step 1. This grants access to read and patch
only that catalog. If you use another namespace or the Bookworm catalog, update
the namespace and catalog name consistently here and in the CronJob command.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: catalog-updater
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: catalog-updater
rules:
  - apiGroups: ["postgresql.cnpg.io"]
    resources: ["clusterimagecatalogs"]
    resourceNames: ["postgresql-minimal-trixie"]
    verbs: ["get", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: catalog-updater
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: catalog-updater
subjects:
  - kind: ServiceAccount
    name: catalog-updater
    namespace: default
```

</details>

`OnFailure` uses Kubernetes restart backoff and the Job's default retry limit.
The community-maintained `alpine/kubectl:latest` image keeps this copy-paste
example from retaining an old kubectl version; new workloads using `:latest`
default to `imagePullPolicy: Always`. If you manage kubectl versions explicitly,
choose one [compatible with your API server](https://kubernetes.io/releases/version-skew-policy/#kubectl).

The catalogs are published daily at 10:00 UTC and after successful extension
builds on `main`. Each refresh incorporates the upstream catalog. Publication
does not update your installed Kubernetes object: the CronJob applies the
latest published manifest on your schedule. You can also rerun the step 1
command manually during maintenance. See the
[catalog publication workflow](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/workflows/update-catalogs.yml).

### SQL extension updates

An updated image supplies new binaries and SQL scripts; do not equate an image
rollout with completion of every database's SQL extension migration. When an
alert fires, review the extension's upgrade instructions and available upgrade
path. For declaratively managed extensions, set the reviewed target `version`
in the relevant `Database.spec.extensions` entry. For extensions managed directly
with SQL, use `ALTER EXTENSION ... UPDATE` in each affected database. Confirm the
installed version and that the alert clears. See
[CNPG's database extension management](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).

Changes only to catalog environment variables or library paths may need an
explicit cluster restart; CNPG does not automatically roll out those changes
alone. See the [runtime configuration caveats](https://cloudnative-pg.io/docs/1.30/imagevolume_extensions/#environment-variables-for-extensions).

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
This classification covers the material shipped in each extension image,
including bundled libraries, rather than only the extension's root license.
The PostgreSQL base image is assessed separately. Consult each recipe and
image's notices and SBOM for license details.

**Debian packages with CNCF-compatible declared licenses:** [credcheck](credcheck), [db2fce](db2fce), [decoderbufs](decoderbufs), [extra-window-functions](extra-window-functions), [first-last-agg](first-last-agg), [hypopg](hypopg), [icu-ext](icu-ext), [ip4r](ip4r), [jsquery](jsquery), [mimeo](mimeo), [orafce](orafce), [periods](periods), [pg-background](pg-background), [pg-csv](pg-csv), [pg-dirtyread](pg-dirtyread), [pg-hint-plan](pg-hint-plan), [pg-partman](pg-partman), [pg-permissions](pg-permissions), [pg-qualstats](pg-qualstats), [pg-rage-terminator](pg-rage-terminator), [pg-repack](pg-repack), [pg-rewrite](pg-rewrite), [pg-similarity](pg-similarity), [pg-squeeze](pg-squeeze), [pg-stat-kcache](pg-stat-kcache), [pg-stat-log](pg-stat-log), [pg-stat-plans](pg-stat-plans), [pg-stat-tcpinfo](pg-stat-tcpinfo), [pg-statviz](pg-statviz), [pg-track-settings](pg-track-settings), [pg-wait-sampling](pg-wait-sampling), [pgextwlist](pgextwlist), [pgfaceting](pgfaceting), [pgfincore](pgfincore), [pglogical](pglogical), [pgnodemx](pgnodemx), [pgpcre](pgpcre), [pgq](pgq), [pgsentinel](pgsentinel), [pgtap](pgtap), [pgtt](pgtt), [pljs](pljs), [pllua](pllua), [plpgsql-check](plpgsql-check), [plproxy](plproxy), [plsh](plsh), [pointcloud](pointcloud), [powa](powa), [prefix](prefix), [preprepare](preprepare), [prioritize](prioritize), [rational](rational), [roaringbitmap](roaringbitmap), [rum](rum), [semver](semver), [set-user](set-user), [show-plans](show-plans), [tdigest](tdigest), [timestamp9](timestamp9), [toastinfo](toastinfo).

**Debian packages outside the CNCF-compatible group:** [age](age), [asn1oid](asn1oid), [debversion](debversion), [h3](h3), [hll](hll), [http](http), [mobilitydb](mobilitydb), [numeral](numeral), [ogr-fdw](ogr-fdw), [pg-cron](pg-cron), [pg-gvm](pg-gvm), [pg-pwhash](pg-pwhash), [pg-rrule](pg-rrule), [pg-uuidv7](pg-uuidv7), [pgmemcache](pgmemcache), [pgmp](pgmp), [pgsphere](pgsphere), [pldebugger](pldebugger), [plprofiler](plprofiler), [pltcl](pltcl), [q3c](q3c), [rdkit](rdkit), [table-log](table-log), [tds-fdw](tds-fdw), [unit](unit).

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
  the [DFSG](https://www.debian.org/social_contract#guidelines)). Extensions added through the Debian framework
  should have packages available for both current Debian `stable` and `oldstable`.
  The [PostgreSQL Global Development Group (PGDG)](https://wiki.postgresql.org/wiki/Apt)
  repository is required in practice to provide matching extension versions for
  both distributions; the regular Debian repositories do not provide this consistency.
  Other third-party APT repositories are not accepted: in our experience their
  packages generally do not meet Debian standards, while packages that meet those
  standards are usually available in Debian. See the
  [Debian packaging policy](source-build/README.md#inclusion-policy-debian-packaging-first)
  for the community, licensing and dependency-management reasons behind this requirement.
  Rust extensions use the [PGRX path](pgrx/README.md);
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

PGRX and Universe build contributors: see the [shared build and local validation guide](./source-build/README.md).
