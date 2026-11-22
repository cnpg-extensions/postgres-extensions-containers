# pg_search
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[ParadeDB](https://github.com/paradedb/paradedb) provides a custom index for
fast full-text and vector search, BM25 scoring, filters, facets,
aggregations, and joins. Use it to search and rank database records while
filtering the results, such as finding items that match both keywords and
categories.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

> [!NOTE]
> This image is **ParadeDB Community**. It supports single-node deployments.
> (`spec.instances:1`)
>
> ParadeDB Enterprise adds support and physical replication for
> ParadeDB indexes, enabling high availability, failover, and read replicas.
> (`spec.instances:2` or more) [ParadeDB Documentation](https://www.paradedb.com/docs/operate/deploy/enterprise)

## Dependencies and conflicts

Requires `vector` in the same database.

For more information, see the [upstream documentation](https://github.com/paradedb/paradedb).

### 1. Add the pg-search extension image to your Cluster

Include both the `pgvector` and `pg-search` extension images in your Cluster.
This extension requires `pg_search` in `shared_preload_libraries`, as shown
below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-search
spec:
  instances: 1
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_search
    extensions:
    - name: pgvector
    - name: pg-search
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION pg_search;
```

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT * FROM paradedb.version_info();
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
