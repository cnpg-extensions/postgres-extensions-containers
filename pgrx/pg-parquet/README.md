# pg_parquet
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_parquet](https://github.com/CrunchyData/pg_parquet) is a PostgreSQL extension for reading and writing Parquet files with
PostgreSQL's `COPY TO/FROM` commands. It supports local files, S3, Azure Blob
Storage, Google Cloud Storage, and HTTP(S) endpoints.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/CrunchyData/pg_parquet).

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
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_parquet
    extensions:
    - name: pg-parquet
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_parquet;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_parquet
```

You should see `pg_parquet` listed with its installed SQL version.

## Known Caveats

- `pg_parquet` must be loaded through `shared_preload_libraries`; the Cluster
  configuration above supplies this setting.
- When also preloading `pg_duckdb`, place `pg_parquet` after it for the
  [COPY hook ordering](../../universe/pg-duckdb/README.md#known-caveats).
- Local `COPY TO` paths must be writable by PostgreSQL. Use a path under the
  writable PostgreSQL data volume rather than `/tmp` on CNPG's read-only root
  filesystem.
- To read from or write to an object store, grant the corresponding
  `parquet_object_store_read` or `parquet_object_store_write` role to the
  PostgreSQL user. Configure credentials using the methods described in the
  [upstream documentation](https://github.com/CrunchyData/pg_parquet#object-store-support).
- The `pg_parquet.enable_copy_hooks` parameter can be set to `off` to disable
  the extension's COPY hooks for a session or role.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
