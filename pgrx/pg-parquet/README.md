# pg_parquet
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Reads and writes Parquet files with PostgreSQL's `COPY TO/FROM` commands.
Use it to move data between database tables and files used by analytics tools.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

## Dependencies and conflicts

Avoid using pg_parquet and [pg_duckdb](../../universe/pg-duckdb/README.md) in
the same cluster. Light testing with pg_duckdb 1.2.0 and pg_parquet 0.5.1
found that DuckDB can intercept Parquet `COPY FROM` intended for pg_parquet.
Other issues may remain undiscovered.

For more information, see the [upstream documentation](https://github.com/CrunchyData/pg_parquet).

### 1. Add the pg-parquet extension image to your Cluster

This extension requires `pg_parquet` in `shared_preload_libraries`, as shown
below.

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

```sql
SELECT extversion FROM pg_extension WHERE extname = 'pg_parquet';
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
