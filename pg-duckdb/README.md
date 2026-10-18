# pg_duckdb
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_duckdb](https://github.com/duckdb/pg_duckdb) embeds the
[DuckDB](https://duckdb.org/) analytical engine in PostgreSQL, to query Parquet,
CSV and JSON files and to run analytical queries on PostgreSQL tables.

PGDG does not ship pg_duckdb, so the image is built from the upstream release
tag with DuckDB linked statically. Images are built for `linux/amd64` and
`linux/arm64`.

## Usage

### 1. Add the pg-duckdb extension image to your Cluster

Define the `pg-duckdb` extension under the `postgresql.extensions` section of
your `Cluster` resource. `pg_duckdb` must be preloaded, and its system
libraries are found through `ld_library_path`. For example:

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
        reference: ghcr.io/cnpg-extensions/pg-duckdb:1.1.1-18-trixie
      ld_library_path: [system]
```

### 2. Enable the extension in a database

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
    version: '1.1.0'
```

Alternatively, run `CREATE EXTENSION pg_duckdb;` in `psql`.

### 3. Verify installation

```sql
\dx
SELECT duckdb.query('select 42');
```

## Contributors

This extension is maintained by:

- Tobias Florek (@ibotty)

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg_duckdb` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
