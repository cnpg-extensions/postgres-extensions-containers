# pg_parquet
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_parquet](https://github.com/CrunchyData/pg_parquet) is a PostgreSQL
extension for reading and writing [Parquet files](https://parquet.apache.org)
with PostgreSQL's `COPY TO/FROM` commands. It supports local files, S3, Azure
Blob Storage, Google Cloud Storage, and HTTP(S) endpoints. This image supports
PostgreSQL 18 on Debian bookworm and trixie.

Follow the [quick start](../../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

### 1. Add the pg-parquet extension image to your Cluster

Define the `pg-parquet` extension under the `postgresql.extensions` section of
your `Cluster` resource. The extension must also be added to
`shared_preload_libraries`. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-parquet
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
    shared_preload_libraries:
    - pg_parquet
    extensions:
    - name: pg-parquet
```

### 2. Enable the extension in a database

You can install `pg_parquet` in a specific database by creating or updating a
`Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-parquet-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-parquet
  extensions:
  - name: pg_parquet
```

Alternatively, enable it directly with SQL:

```sql
CREATE EXTENSION pg_parquet;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_parquet` listed with its installed SQL version.

## Known Caveats

- `pg_parquet` must be loaded through `shared_preload_libraries`; the Cluster
  configuration above supplies this setting.
- When also preloading `pg_duckdb`, place `pg_parquet` after it for the
  [tested COPY behavior](../../universe/pg-duckdb/README.md#known-caveats).
- Local `COPY TO` paths must be writable by PostgreSQL. CNPG's read-only root
  filesystem rejected `/tmp` in runtime testing; a path under the writable
  PostgreSQL data volume passed the write/read roundtrip.
- To read from or write to an object store, grant the corresponding
  `parquet_object_store_read` or `parquet_object_store_write` role to the
  PostgreSQL user. Configure credentials using the methods described in the
  [upstream documentation](https://github.com/CrunchyData/pg_parquet#object-store-support).
- The `pg_parquet.enable_copy_hooks` parameter can be set to `off` to disable
  the extension's COPY hooks for a session or role.

## Contributors

Maintained by Jeremy Schneider ([@ardentperf](https://github.com/ardentperf)).

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.

The extension uses the [PostgreSQL License](https://github.com/CrunchyData/pg_parquet/blob/v0.5.1/LICENSE).
