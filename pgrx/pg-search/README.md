# pg_search
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_search](https://github.com/paradedb/paradedb) (also known as ParadeDB)
provides a custom index for fast full-text and vector
search, BM25 scoring, filters, facets, aggregations, and joins. It keeps your
application data and search engine in one database with standard SQL and ACID
transactions.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

> [!NOTE]
> This image is **ParadeDB Community**. It supports single-node deployments.
> (`spec.instances:1`)
>
> ParadeDB Enterprise adds support and physical replication for
> ParadeDB indexes, enabling high availability, failover, and read replicas.
> (`spec.instances:2` or more) [ParadeDB Documentation](https://www.paradedb.com/docs/operate/deploy/enterprise)

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
  instances: 1
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_search
    extensions:
    - name: pgvector
    - name: pg-search
```

`pg_search` also requires the `vector` extension for the vector types used by its
vector search functionality. The example selects `pgvector` from the same
catalog. Install `vector` before `pg_search` in the database.

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

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
