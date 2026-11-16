# pg_search
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_search](https://github.com/paradedb/paradedb) is a
PostgreSQL extension for fast full-text, faceted, and hybrid search over
PostgreSQL tables using the BM25 algorithm and Tantivy. This image supports
PostgreSQL 18 on Debian bookworm and trixie.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

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
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_search
    extensions:
    - name: pgvector
    - name: pg-search
```

`pg_search` also requires the `vector` extension. The example selects `pgvector`
from the same catalog. Install `vector` before `pg_search` in the database.

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_search;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

Install `vector`, then `pg_search` in that order.

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

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
