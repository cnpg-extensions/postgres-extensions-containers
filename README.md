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

| Extension | Description | Project URL | Maintained by | License blocker |
| :--- | :--- | :--- | :--- | :--- |
| **[age](age)** | Apache AGE graph database extension (Cypher queries) | [github.com/apache/age](https://github.com/apache/age) | @ardentperf | libcsv (LGPL-2.1+) |
| **[asn1oid](asn1oid)** | ASN.1 object identifiers as a native PostgreSQL type | [github.com/df7cb/pgsql-asn1oid](https://github.com/df7cb/pgsql-asn1oid) | @ardentperf | GPL-3.0-or-later |
| **[credcheck](credcheck)** | PostgreSQL username and password checks | [github.com/MigOpsRepos/credcheck](https://github.com/MigOpsRepos/credcheck) | @ardentperf | MIT |
| **[db2fce](db2fce)** | DB2-compatible SQL functions and types | [github.com/credativ/db2fce](https://github.com/credativ/db2fce) | @ardentperf | PostgreSQL |
| **[debversion](debversion)** | Debian package version comparison type | [salsa.debian.org/postgresql/postgresql-debversion](https://salsa.debian.org/postgresql/postgresql-debversion) | @ardentperf | GPL-3+ |
| **[decoderbufs](decoderbufs)** | Logical decoding output serialized as Protocol Buffers | [github.com/debezium/postgres-decoderbufs](https://github.com/debezium/postgres-decoderbufs) | @ardentperf | MIT |
| **[extra-window-functions](extra-window-functions)** | Window functions including lag and lead that ignore nulls | [github.com/xocolatl/extra_window_functions](https://github.com/xocolatl/extra_window_functions) | @ardentperf | PostgreSQL |
| **[first-last-agg](first-last-agg)** | first() and last() ordered aggregates | [github.com/wulczer/first_last_agg](https://github.com/wulczer/first_last_agg) | @ardentperf | PostgreSQL |
| **[h3](h3)** | Uber H3 hexagonal geospatial indexing | [github.com/zachasme/h3-pg](https://github.com/zachasme/h3-pg) | @ardentperf | libh3-1 (Apache-2.0 + AGPL-3+ test deps) |
| **[hll](hll)** | HyperLogLog types and aggregates for approximate distinct counts | [github.com/citusdata/postgresql-hll](https://github.com/citusdata/postgresql-hll) | @ardentperf | Apache-2.0 |
| **[http](http)** | HTTP client functions callable from SQL | [github.com/pramsey/pgsql-http](https://github.com/pramsey/pgsql-http) | @ardentperf | MIT |
| **[hypopg](hypopg)** | Hypothetical index support | [github.com/HypoPG/hypopg](https://github.com/HypoPG/hypopg) | @ardentperf | PostgreSQL License |
| **[icu-ext](icu-ext)** | ICU text transformation, comparison, collation, and Unicode functions | [github.com/dverite/icu_ext](https://github.com/dverite/icu_ext) | @ardentperf | LicenseRef-verite |
| **[ip4r](ip4r)** | IPv4 and IPv6 address and range types with operators and indexing | [github.com/RhodiumToad/ip4r](https://github.com/RhodiumToad/ip4r) | @ardentperf | PostgreSQL |
| **[jsquery](jsquery)** | jsquery language and GIN indexing for jsonb searches | [github.com/postgrespro/jsquery](https://github.com/postgrespro/jsquery) | @ardentperf | PostgreSQL |
| **[mimeo](mimeo)** | Per-table replication using snapshot, incremental, and DML-based methods | [pgxn.org/dist/mimeo/1.5.1/doc/mimeo.html](https://pgxn.org/dist/mimeo/1.5.1/doc/mimeo.html) | @ardentperf | PostgreSQL |
| **[mobilitydb](mobilitydb)** | Spatio-temporal moving objects database | [mobilitydb.com](https://mobilitydb.com/) | @ardentperf | GPL-2+, GPL-3+ |
| **[mysql-fdw](mysql-fdw)** | MySQL/MariaDB foreign data wrapper | [github.com/EnterpriseDB/mysql_fdw](https://github.com/EnterpriseDB/mysql_fdw) | @ardentperf | libmariadb3 (LGPL-2.1) |
| **[numeral](numeral)** | Compact numeral type with arithmetic, comparison, and bitwise operators | [github.com/df7cb/postgresql-numeral](https://github.com/df7cb/postgresql-numeral) | @ardentperf | GPL-2.0-or-later |
| **[ogr-fdw](ogr-fdw)** | Foreign data wrapper for GDAL/OGR vector data sources | [github.com/pramsey/pgsql-ogr-fdw](https://github.com/pramsey/pgsql-ogr-fdw) | @ardentperf | MIT |
| **[orafce](orafce)** | Oracle-compatible SQL functions and packages, including NVL | [github.com/orafce/orafce](https://github.com/orafce/orafce) | @ardentperf | 0BSD, GPL-3.0-or-later WITH Bison-exception-2.2 |
| **[periods](periods)** | SQL periods and system versioning for PostgreSQL | [github.com/xocolatl/periods](https://github.com/xocolatl/periods) | @ardentperf | PostgreSQL |
| **[pg-background](pg-background)** | Run SQL in background workers and return completion metadata | [github.com/vibhorkum/pg_background](https://github.com/vibhorkum/pg_background) | @ardentperf | PostgreSQL |
| **[pg-cron](pg-cron)** | Cron-based job scheduler for PostgreSQL | [github.com/citusdata/pg_cron](https://github.com/citusdata/pg_cron) | @ardentperf | Vixie-Cron (src/entry.c, src/misc.c) |
| **[pg-csv](pg-csv)** | Flexible CSV processing functions for PostgreSQL | [github.com/PostgREST/pg_csv](https://github.com/PostgREST/pg_csv/) | @ardentperf | MIT |
| **[pg-dirtyread](pg-dirtyread)** | Read dead, unvacuumed tuples from a PostgreSQL relation | [github.com/df7cb/pg_dirtyread](https://github.com/df7cb/pg_dirtyread) | @ardentperf | BSD-3-Clause |
| **[pg-gvm](pg-gvm)** | Greenbone helper functions for host matching, regular expressions, and schedules | [github.com/greenbone/pg-gvm](https://github.com/greenbone/pg-gvm) | @ardentperf | GPL-3.0-or-later, AGPL-3.0-or-later |
| **[pg-hint-plan](pg-hint-plan)** | Query optimizer hints in SQL comments | [github.com/ossc-db/pg_hint_plan](https://github.com/ossc-db/pg_hint_plan) | @ardentperf | NTT |
| **[pg-partman](pg-partman)** | Time- and ID-based partition management | [github.com/pgpartman/pg_partman](https://github.com/pgpartman/pg_partman) | @ardentperf | PostgreSQL License |
| **[pg-permissions](pg-permissions)** | Inspect permissions in a PostgreSQL database | [github.com/cybertec-postgresql/pg_permissions](https://github.com/cybertec-postgresql/pg_permissions) | @ardentperf | PostgreSQL |
| **[pg-pwhash](pg-pwhash)** | Adaptive Argon2, scrypt, and yescrypt password-hashing functions | [github.com/cybertec-postgresql/pg_pwhash](https://github.com/cybertec-postgresql/pg_pwhash) | @ardentperf | MIT |
| **[pg-qualstats](pg-qualstats)** | Predicate and missing-index statistics | [github.com/powa-team/pg_qualstats](https://github.com/powa-team/pg_qualstats) | @ardentperf | PostgreSQL License |
| **[pg-rage-terminator](pg-rage-terminator)** | Terminate random sessions for chaos testing | [github.com/disco-stu/pg_rage_terminator](https://github.com/disco-stu/pg_rage_terminator) | @ardentperf | PostgreSQL |
| **[pg-repack](pg-repack)** | Rebuild tables and indexes while allowing normal reads and writes | [github.com/reorg/pg_repack](https://github.com/reorg/pg_repack) | @ardentperf | BSD-3-Clause |
| **[pg-rewrite](pg-rewrite)** | Rewrite PostgreSQL tables with less locking | [github.com/cybertec-postgresql/pg_rewrite](https://github.com/cybertec-postgresql/pg_rewrite) | @ardentperf | PostgreSQL |
| **[pg-rrule](pg-rrule)** | iCalendar RRULE recurrence rule type | [github.com/petropavel13/pg_rrule](https://github.com/petropavel13/pg_rrule) | @ardentperf | libical3 (LGPL-2.1/MPL-2.0) |
| **[pg-similarity](pg-similarity)** | Similarity functions for PostgreSQL | [github.com/eulerto/pg_similarity](https://github.com/eulerto/pg_similarity) | @ardentperf | BSD-3-Clause |
| **[pg-squeeze](pg-squeeze)** | Online table bloat cleanup (pg_squeeze) | [github.com/cybertec-postgresql/pg_squeeze](https://github.com/cybertec-postgresql/pg_squeeze) | @ardentperf | PostgreSQL License |
| **[pg-stat-kcache](pg-stat-kcache)** | Per-query kernel and filesystem statistics | [github.com/powa-team/pg_stat_kcache](https://github.com/powa-team/pg_stat_kcache) | @ardentperf | PostgreSQL License |
| **[pg-stat-log](pg-stat-log)** | Cumulative server-log message counts grouped by backend and message attributes | [github.com/fabriziomello/pg_stat_log](https://github.com/fabriziomello/pg_stat_log) | @ardentperf | PostgreSQL |
| **[pg-stat-plans](pg-stat-plans)** | Per-plan execution statistics and EXPLAIN texts | [github.com/pganalyze/pg_stat_plans](https://github.com/pganalyze/pg_stat_plans) | @ardentperf | Duboce/PostgreSQL-style license |
| **[pg-statviz](pg-statviz)** | Capture PostgreSQL statistics in tables for later SQL analysis | [github.com/vyruss/pg_statviz](https://github.com/vyruss/pg_statviz) | @ardentperf | PostgreSQL |
| **[pg-track-settings](pg-track-settings)** | Track PostgreSQL configuration settings | [powa.readthedocs.io](https://powa.readthedocs.io/) | @ardentperf | PostgreSQL |
| **[pg-uuidv7](pg-uuidv7)** | UUID version 7 (time-sortable) generator | [github.com/fboulnois/pg_uuidv7](https://github.com/fboulnois/pg_uuidv7) | @ardentperf | MPL-2.0 |
| **[pg-wait-sampling](pg-wait-sampling)** | Sample wait events and expose historical and aggregated profiles | [github.com/postgrespro/pg_wait_sampling](https://github.com/postgrespro/pg_wait_sampling) | @ardentperf | PostgreSQL |
| **[pgextwlist](pgextwlist)** | PostgreSQL extension whitelisting | [github.com/dimitri/pgextwlist](https://github.com/dimitri/pgextwlist) | @ardentperf | PostgreSQL |
| **[pgfincore](pgfincore)** | PostgreSQL functions to manage relation blocks in memory | [villemain.org/projects/pgfincore](http://villemain.org/projects/pgfincore) | @ardentperf | BSD-3-Clause |
| **[pglogical](pglogical)** | Logical replication over PostgreSQL connections | [github.com/2ndQuadrant/pglogical](https://github.com/2ndQuadrant/pglogical) | @ardentperf | PostgreSQL |
| **[pgmemcache](pgmemcache)** | Memcached client interface for PostgreSQL | [github.com/ohmu/pgmemcache](https://github.com/ohmu/pgmemcache) | @ardentperf | libmemcached11 (LGPL) |
| **[pgmp](pgmp)** | GMP arbitrary-precision arithmetic types | [github.com/dvarrazzo/pgmp](https://github.com/dvarrazzo/pgmp) | @ardentperf | LGPL-3+ |
| **[pgnodemx](pgnodemx)** | Capture operating-system metrics from PostgreSQL | [github.com/pgnodemx/pgnodemx](https://github.com/pgnodemx/pgnodemx) | @ardentperf | PostgreSQL, Apache-2.0 |
| **[pgpcre](pgpcre)** | PCRE2-backed regular-expression type and capture functions | [github.com/petere/pgpcre](https://github.com/petere/pgpcre) | @ardentperf | PostgreSQL |
| **[pgq](pgq)** | Transactional, lockless event queue with SQL and PostgreSQL C helpers | [github.com/pgq/pgq](https://github.com/pgq/pgq) | @ardentperf | ISC |
| **[pgsentinel](pgsentinel)** | Active session history sampler | [github.com/pgsentinel/pgsentinel](https://github.com/pgsentinel/pgsentinel) | @ardentperf | PgSentinel PostgreSQL-style license |
| **[pgsphere](pgsphere)** | Spherical geometry for astronomical data | [pgsphere.github.io](https://pgsphere.github.io/) | @ardentperf | GPL-3+ |
| **[pgtap](pgtap)** | Unit testing framework for PostgreSQL | [pgtap.org](https://pgtap.org/) | @ardentperf | PostgreSQL |
| **[pgtt](pgtt)** | Global temporary tables for PostgreSQL | [github.com/darold/pgtt](https://github.com/darold/pgtt/) | @ardentperf | ISC |
| **[pldebugger](pldebugger)** | PL/pgSQL interactive debugger (pldbgapi) | [github.com/EnterpriseDB/pldebugger](https://github.com/EnterpriseDB/pldebugger) | @ardentperf | Artistic-2.0 |
| **[pljs](pljs)** | Trusted JavaScript procedural language backed by QuickJS | [github.com/plv8/pljs](https://github.com/plv8/pljs) | @ardentperf | LicenseRef-PLJS |
| **[pllua](pllua)** | Trusted and untrusted PL/Lua languages with optional hstore transform | [pllua.github.io/pllua](https://pllua.github.io/pllua/) | @ardentperf | MIT |
| **[plprofiler](plprofiler)** | PL/pgSQL execution profiler | [github.com/bigsql/plprofiler](https://github.com/bigsql/plprofiler) | @ardentperf | Artistic-2.0 |
| **[plpgsql-check](plpgsql-check)** | PL/pgSQL linter and static checker | [github.com/okbob/plpgsql_check](https://github.com/okbob/plpgsql_check) | @ardentperf | MIT |
| **[plproxy](plproxy)** | Database partitioning system for PostgreSQL | [plproxy.github.io](https://plproxy.github.io/) | @ardentperf | ISC |
| **[plsh](plsh)** | PL/sh procedural language for PostgreSQL | [github.com/petere/plsh](https://github.com/petere/plsh) | @ardentperf | PostgreSQL |
| **[pltcl](pltcl)** | Tcl procedural language for PostgreSQL | [www.postgresql.org/docs/18/pltcl.html](https://www.postgresql.org/docs/18/pltcl.html) | @ardentperf | PostgreSQL, TCL |
| **[pointcloud](pointcloud)** | Types and functions for storing and querying LiDAR point-cloud data | [github.com/pgpointcloud/pointcloud](https://github.com/pgpointcloud/pointcloud) | @ardentperf | BSD-3-Clause |
| **[powa](powa)** | Workload Analyzer history and snapshot schema | [powa.readthedocs.io/en/stable](https://powa.readthedocs.io/en/stable/) | @ardentperf | PostgreSQL |
| **[prefix](prefix)** | Prefix ranges for text lookup and indexing | [github.com/dimitri/prefix](https://github.com/dimitri/prefix) | @ardentperf | BSD-2-Clause |
| **[preprepare](preprepare)** | Pre-prepare PostgreSQL statements on the server side | [github.com/dimitri/preprepare](https://github.com/dimitri/preprepare) | @ardentperf | PostgreSQL |
| **[prioritize](prioritize)** | Get and set the nice priorities of PostgreSQL backends | [pgxn.org/dist/prioritize](http://pgxn.org/dist/prioritize/) | @ardentperf | PostgreSQL |
| **[q3c](q3c)** | Quad Tree Cube sky survey spatial indexing | [github.com/segasai/q3c](https://github.com/segasai/q3c) | @ardentperf | GPL-2+ |
| **[rational](rational)** | Exact integer-fraction arithmetic for PostgreSQL | [github.com/begriffs/pg_rational](https://github.com/begriffs/pg_rational) | @ardentperf | MIT |
| **[rdkit](rdkit)** | Cheminformatics types and functions for PostgreSQL | [github.com/rdkit/rdkit](https://github.com/rdkit/rdkit) | @ardentperf | BSD-3-Clause |
| **[roaringbitmap](roaringbitmap)** | Compressed Roaring bitmap data structures and set operations | [github.com/ChenHuajun/pg_roaringbitmap](https://github.com/ChenHuajun/pg_roaringbitmap) | @ardentperf | Apache-2.0 |
| **[rum](rum)** | RUM index access method for full-text search and ordering | [github.com/postgrespro/rum](https://github.com/postgrespro/rum) | @ardentperf | PostgreSQL |
| **[semver](semver)** | Semantic-version data type with comparison and ordering operators | [pgxn.org/dist/semver/doc/semver.html](https://pgxn.org/dist/semver/doc/semver.html) | @ardentperf | PostgreSQL |
| **[set-user](set-user)** | PostgreSQL privilege escalation with enhanced logging and control | [github.com/pgaudit/set_user](https://github.com/pgaudit/set_user) | @ardentperf | PostgreSQL |
| **[show-plans](show-plans)** | Query plans for currently running statements | [github.com/cybertec-postgresql/pg_show_plans](https://github.com/cybertec-postgresql/pg_show_plans) | @ardentperf | Cybertec PostgreSQL-style license |
| **[table-log](table-log)** | Log table changes and restore tables to a point in time | [github.com/df7cb/table_log](https://github.com/df7cb/table_log) | @ardentperf | LicenseRef-table-log |
| **[tdigest](tdigest)** | t-digest aggregates for approximate quantile and percentile calculations | [github.com/tvondra/tdigest](https://github.com/tvondra/tdigest) | @ardentperf | PostgreSQL |
| **[tds-fdw](tds-fdw)** | Microsoft SQL Server / Sybase foreign data wrapper | [github.com/tds-fdw/tds_fdw](https://github.com/tds-fdw/tds_fdw) | @ardentperf | libsybdb5/FreeTDS (LGPL-2+) |
| **[timestamp9](timestamp9)** | Timestamp type with nanosecond precision | [github.com/optiver/timestamp9](https://github.com/optiver/timestamp9) | @ardentperf | MIT |
| **[unit](unit)** | SI unit values, conversions, and arithmetic | [github.com/df7cb/postgresql-unit](https://github.com/df7cb/postgresql-unit) | @ardentperf | GPL-3.0-or-later |

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

Renovate automatically merges eligible minor, patch, and digest updates once
required checks pass. Major updates and packages without a verified SQL version
mapping require manual review. Packages containing independently versioned SQL
extensions also require manual review. The Automerge gate checks extension
updates for prerelease version markers, with an exception for AGE's release
naming.

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

## SBOMs and authenticity

Use the [SBOM guide](./sbom-generator/README.md) to verify an extension image,
extract its platform-specific SPDX, and report vulnerabilities and licenses with
Grype and Grant. See the [example report](./examples/sbom-reports.txt) and
[generator release workflow](./sbom-generator/README.md#generator-release-and-test-builds).

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
