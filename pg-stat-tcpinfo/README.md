# pg_stat_tcpinfo
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Live Linux TCP socket statistics exposed through SQL. [Upstream documentation](https://github.com/jakubwartakEDB/pg_stat_tcpinfo).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Supported images

PostgreSQL 18 on Debian Bookworm and Trixie, for amd64 and arm64.

## Usage

### 1. Add the pg-stat-tcpinfo extension image to your Cluster

Define `pg-stat-tcpinfo` under `postgresql.extensions`.
No shared preload configuration is needed.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-tcpinfo
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-stat-tcpinfo
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_stat_tcpinfo;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

## Query TCP statistics

As an administrator, grant monitoring access to the application role:

```sql
GRANT pg_monitor TO app;
```

Connect over TCP as that role, then query:

```sql
SELECT pid, src_addr, src_port, dst_addr, dst_port, state,
       tcpinfo->>'rtt' AS rtt
FROM pg_stat_tcpinfo
WHERE state = 'ESTABLISHED'
ORDER BY pid;
```

The extension reports sockets owned by PostgreSQL's OS user within the pod's
network namespace. It requires Linux procfs and netlink socket diagnostics;
restricted sandbox policies can prevent collection. No extra Linux capabilities
are required in the tested stock CNPG environment. UNIX-domain connections do
not appear as TCP sockets; use a TCP connection when verifying the view.

Access is restricted to `pg_read_all_stats` (also inherited by `pg_monitor`),
not PUBLIC. These monitoring roles expose additional database statistics;
grant them only to appropriate users. No persistent files or maintenance daemon
are needed.

## Licenses and Copyright

The extension and Debian packaging use the **PostgreSQL** license. The full
copyright and license notice is shipped at
`/licenses/postgresql-18-pg-stat-tcpinfo/copyright`.

The image contains the extension library, its LLVM bitcode, SQL/control files,
and notice. It bundles no system libraries: libc and the ELF loader come from
the matching PostgreSQL base image. The payload belongs in the top-level
README's CNCF-compatible declared-license group; this classification describes
licenses, not a claim of upstream CNCF project acceptance.

## Updates and validation

Renovate tracks Debian package pins and SQL versions in `metadata.hcl`. SQL
versions are extracted from the verified package version shape; review the
packaged control files and upgrade scripts when that shape changes. Rebuild
and validate both distributions and architectures after package updates.

The extension-specific Chainsaw test exercises real behavior through the mounted
image, in addition to the shared installation checks. Run:

```sh
task checks TARGET=pg-stat-tcpinfo
task e2e:test:full TARGET=pg-stat-tcpinfo
```
