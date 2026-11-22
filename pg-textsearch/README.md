# pg_textsearch
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides full-text search with BM25 relevance ranking. Use it to search
stored text and show the most relevant matches first, such as matching
articles or descriptions.

For more information, see the [upstream documentation](https://github.com/timescale/pg_textsearch).

## Dependencies and conflicts

Background compaction requires `pg_durable` 0.2.8 or later in the same database.

### 1. Add the pg-textsearch extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This example uses [pg_durable](../pgrx/pg-durable/README.md) for background
index compaction in the `app` database. Both extensions must be preloaded.
CNPG manages `workflow_runner`, the login that owns the example index and
runs its compaction workflows. HTTP activities are disabled.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-textsearch
spec:
  imageCatalogRef: ...
  managed:
    roles:
    - name: workflow_runner
      login: true
  postgresql:
    parameters:
      pg_durable.database: app
      pg_durable.http_security: disabled
    pg_ident:
    - local postgres workflow_runner
    shared_preload_libraries:
    - pg_durable
    - pg_textsearch
    extensions:
    - name: pg-durable
    - name: pg-textsearch
```

### 2. Enable the extension in a database

As an administrator in `app`, install both extensions and prepare a schema
owned by the workflow runner:

```sql
CREATE EXTENSION IF NOT EXISTS pg_durable;
CREATE EXTENSION pg_textsearch;
SELECT df.grant_usage('workflow_runner');
CREATE SCHEMA search AUTHORIZATION workflow_runner;
```

### 3. Verify installation

As `workflow_runner` in `app`, create and query an index with background
compaction enabled:

```sql
SET search_path TO search, public;
CREATE TABLE documents (id bigint PRIMARY KEY, content text);
INSERT INTO documents VALUES
  (1, 'PostgreSQL database search'),
  (2, 'BM25 relevance ranking');
CREATE INDEX documents_bm25 ON documents USING bm25(content)
  WITH (text_config = 'english', compaction = 'background');
SELECT id, content FROM documents
ORDER BY content <@> 'database search'
LIMIT 5;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
