# pg_search
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_search](https://github.com/paradedb/paradedb) is a
PostgreSQL extension for fast full-text, faceted, and hybrid search over
PostgreSQL tables using the BM25 algorithm and Tantivy. This image supports
PostgreSQL 18 on Debian bookworm and trixie.

Follow the [quick start](../../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

### 1. Add the pg-search extension image to your Cluster

Define the `pg-search` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-search
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
    - pg_search
    extensions:
    - name: pgvector
    - name: pg-search
```

`pg_search` also requires the `vector` extension. The example selects `pgvector`
from the same catalog and installs `vector` before `pg_search` below.

### 2. Enable the extension in a database

You can install `pg_search` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For
example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-search-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-search
  extensions:
  - name: vector
  - name: pg_search
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_search CASCADE;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_search
```

You should see `pg_search` listed with its installed SQL version. The extension must be
included in `shared_preload_libraries`; the Cluster example above supplies this
setting explicitly because preloads are not inherited from the catalog.

## Known Caveats

- `pg_search` requires `vector` from [pgvector](https://github.com/pgvector/pgvector).
  Install or mount pgvector before creating `pg_search`.
- With pg_search 0.26.6 preloaded, creating pg_duckdb 1.2.0 before
  pg_search in the same connection can make `CREATE INDEX ... USING paradedb`
  fail with `XX000: relation is not a ParadeDB index`, even with
  `duckdb.force_execution = off`. On native AMD64 PostgreSQL 18 / Trixie /
  CNPG 1.30.1, creating pg_search before pg_duckdb or reconnecting after
  extension installation passed the BM25 match, ranking, and index-maintenance
  assertions. An eleven-extension composition plus pgvector passed
  with that connection boundary and the original preload order. `DISCARD ALL`
  did not resolve the same-session failure. This is an installation-session
  limitation; reconnecting avoids it without disabling extension hooks or
  weakening the search checks. Other platforms were not tested for this issue.

## Contributors

Maintained by Jeremy Schneider (@ardentperf).

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
