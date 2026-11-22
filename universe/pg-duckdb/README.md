# pg_duckdb
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Integrates DuckDB's analytical query engine with PostgreSQL. Use it to
summarize large datasets with SQL, such as calculating totals across
millions of records.

For more information, see the [upstream documentation](https://github.com/duckdb/pg_duckdb).

## Dependencies and conflicts

Avoid using pg_duckdb and [pg_parquet](../../pgrx/pg-parquet/README.md) in the
same cluster. Light testing with pg_duckdb 1.2.0 and pg_parquet 0.5.1
found that DuckDB can intercept Parquet `COPY FROM` intended for pg_parquet.
Other issues may remain undiscovered.

PL/pgSQL: DuckDB execution inside functions is disabled by default because
it can cause crashes; see the [upstream limitation](https://github.com/duckdb/pg_duckdb/blob/v1.2.0/docs/settings.md#duckdbunsafe_allow_execution_inside_functions).

### 1. Add the pg-duckdb extension image to your Cluster

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pg_duckdb` in `shared_preload_libraries`, as shown
below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-duckdb
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_duckdb
    extensions:
    - name: pg-duckdb
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_duckdb;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run:

```sql
SELECT * FROM duckdb.query('SELECT version()');
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
