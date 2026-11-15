# pg_duckdb
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_duckdb](https://github.com/duckdb/pg_duckdb) integrates DuckDB's analytical
query engine with PostgreSQL. It supports analytical queries over PostgreSQL
tables and external data. This image supports PostgreSQL 18 on Debian trixie,
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
        reference: ghcr.io/cnpg-extensions/pg-duckdb:1.2.0-18-trixie
      ld_library_path: [lib]
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
  cluster requires PostgreSQL to restart. Keep `ld_library_path: [lib]` so the
  extension can load its bundled runtime libraries, including libcurl.
- DuckDB execution defaults to superusers. Review upstream's role and secret
  access settings before granting access through `duckdb.allowed_role`.
- Temporary files and downloaded extensions use `$PGDATA/pg_duckdb/temp` and
  `$PGDATA/pg_duckdb/extensions`. The PostgreSQL user needs write access to these
  directories. Superusers can configure `duckdb.temporary_directory` and
  `duckdb.extension_directory`.
- The image includes DuckDB's json, icu and httpfs extensions. Optional extensions
  downloaded at runtime are not covered by the image's SBOM or bundled notices.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
