# pg_duckdb
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_duckdb](https://github.com/duckdb/pg_duckdb) integrates DuckDB's analytical
query engine with PostgreSQL. It supports analytical queries over PostgreSQL
tables and external data. This image supports PostgreSQL 18
for AMD64 and ARM64.

## Usage

### 1. Add the pg-duckdb extension image to your Cluster

Define the extension under `postgresql.extensions` and preload `pg_duckdb`:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-duckdb
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
    - pg_duckdb

    extensions:
    - name: pg-duckdb
      image:
        # renovate: datasource=github-releases depName=duckdb/pg_duckdb versioning=semver depType=universe-source
        reference: ghcr.io/cnpg-extensions/pg-duckdb:1.2.0-18-trixie
      ld_library_path: [system]
```

### 2. Enable the extension in a database

Create or update a `Database` resource to install the extension in `app`:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-duckdb-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-duckdb
  extensions:
  - name: pg_duckdb
    # renovate: datasource=github-releases depName=duckdb/pg_duckdb versioning=semver depType=universe-source
    version: '1.2.0'
```

Alternatively, run the following SQL as a superuser:

```sql
CREATE EXTENSION pg_duckdb;
```

### 3. Verify installation

Connect to the database with `psql` and run:

```sql
\dx
```

You should see `pg_duckdb` listed among the installed extensions. See the
[upstream documentation](https://github.com/duckdb/pg_duckdb/tree/v1.2.0/docs)
for querying with DuckDB and accessing external data.

## Known Caveats

- `pg_duckdb` requires `shared_preload_libraries`; adding it to an existing
  cluster requires PostgreSQL to restart. Keep `ld_library_path: [system]` so the
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
  after `pg_duckdb` in `shared_preload_libraries`. On CNPG 1.30.1 / PostgreSQL
  18.7 (Trixie, AMD64), the reverse order let DuckDB intercept Parquet
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
