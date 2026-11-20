# pg_duckdb
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pg_duckdb integrates DuckDB's analytical query engine with PostgreSQL. It
supports analytical queries over PostgreSQL tables and external data.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the pg-duckdb extension image to your Cluster

Define the extension under `postgresql.extensions` and preload `pg_duckdb`:

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

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run:

```sql
\dx pg_duckdb
```

You should see `pg_duckdb` listed with its installed SQL version. See the
[upstream documentation](https://github.com/duckdb/pg_duckdb/tree/v1.2.0/docs)
for querying with DuckDB and accessing external data.

## Known Caveats

- `pg_duckdb` requires `shared_preload_libraries`; adding it to an existing
  cluster requires PostgreSQL to restart. The catalog supplies `ld_library_path: [system]` so the
  extension can load its bundled DuckDB shared library.
- DuckDB execution defaults to superusers. Review upstream's role and secret
  access settings before granting access through `duckdb.allowed_role`.
- Temporary files and downloaded extensions use `$PGDATA/pg_duckdb/temp` and
  `$PGDATA/pg_duckdb/extensions`. The PostgreSQL user needs write access to these
  directories. Superusers can configure `duckdb.temporary_directory` and
  `duckdb.extension_directory`.
- The image includes DuckDB's json and icu extensions. Loadable extensions such as httpfs
  downloaded at runtime are not covered by the image's SBOM or bundled notices.

- When combining pg_duckdb 1.2.0 with pg_parquet 0.5.1, put `pg_parquet`
  after `pg_duckdb` in `shared_preload_libraries`. On CNPG 1.30.1 / PostgreSQL 18 (Trixie, AMD64), the reverse order let DuckDB intercept Parquet
  `COPY FROM` into a PostgreSQL table and reject it as unsupported. Loading
  Parquet last passed the tested Parquet write/read roundtrip and DuckDB query.
  This is an observed hook-order integration constraint.
- In that same environment, top-level `EXPLAIN (FORMAT JSON)` of a forced
  DuckDB query succeeded, but executing it dynamically inside PL/pgSQL raised
  `INTERNAL Error: Attempted to access index 1 within vector of size 1`
  from `PGDuckDB/Duckdb_ExplainCustomScan_Cpp`. Use top-level EXPLAIN for this
  diagnostic; the dynamic EXPLAIN failure remains unresolved. These runtime
  findings do not establish an image packaging defect.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
