# pg_textsearch
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pg_textsearch is a PostgreSQL extension for full-text search with BM25 relevance
ranking.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the pg-textsearch extension image to your Cluster

Define the `pg-textsearch` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-textsearch
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_textsearch
    parameters:
      hot_standby_feedback: "on"
    extensions:
    - name: pg-textsearch
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_textsearch;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

For declarative installation, use:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-textsearch-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-textsearch
  extensions:
  - name: pg_textsearch
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_textsearch
```

You should see `pg_textsearch` listed with its installed SQL version. The extension must be
included in `shared_preload_libraries`; the Cluster example above supplies this
setting explicitly because preloads are not inherited from the catalog.

### 4. Create and query an index

```sql
CREATE TABLE documents (id bigint PRIMARY KEY, content text);
INSERT INTO documents VALUES
  (1, 'PostgreSQL database search'),
  (2, 'BM25 relevance ranking');
CREATE INDEX documents_bm25 ON documents USING bm25(content)
  WITH (text_config = 'english');
SELECT id, content FROM documents
ORDER BY content <@> 'database search'
LIMIT 5;
```

Lower (negative) scores rank first. Inspect the plan with `EXPLAIN`; PostgreSQL
may choose a sequential scan for small tables.

## Optional managed background compaction

This image does not bundle pg_durable. The default `inline` compaction mode does
not require it. Managed `background` mode is an upstream preview feature and
requires pg_durable 0.2.8 or later in the same database.

To use our separate [pg-durable image](../pgrx/pg-durable/README.md), add
`pg-durable` to `postgresql.extensions`, add `pg_durable` to
`shared_preload_libraries`, and set `pg_durable.database` in
`postgresql.parameters` to the target database (for example, `app`). Install
both extensions there. The index owner must have `LOGIN` and pg_durable usage
privileges, granted by an administrator with `SELECT df.grant_usage('app');`
when the owner is `app`. Superuser-owned workflows require an additional
pg_durable setting; this example uses a non-superuser owner.

Configure authentication for pg_durable's management and index-owner connections
before enabling background mode; see its [authentication caveats](../pgrx/pg-durable/README.md#known-caveats).
As the index owner, enable it on an existing index with:

```sql
ALTER INDEX documents_bm25 SET (compaction = 'background');
```

Return to explicit maintenance with `compaction = 'manual'`, or to foreground
compaction with `compaction = 'inline'`. See the
[upstream background-compaction documentation](https://github.com/timescale/pg_textsearch/blob/v1.5.1/README.md#background-compaction)
for scheduling and workflow lifecycle details.

## Replication and recovery

Keep `hot_standby_feedback = on` when replicas serve search queries. Upstream
requires this so active replica snapshots delay index page reuse on the primary.
The Cluster example supplies it explicitly. The index is WAL-logged; its
shared-memory cache is rebuilt from persisted index data.
See the [versioned upstream documentation](https://github.com/timescale/pg_textsearch/blob/v1.5.1/README.md#compaction).

Clients must reconnect when CNPG closes connections during a role change.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
