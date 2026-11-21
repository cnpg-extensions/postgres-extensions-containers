# pg-partman
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Creates and maintains time-based and ID-based PostgreSQL partition
sets. Its optional background worker can run partition maintenance
automatically.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/pgpartman/pg_partman).

### 1. Add the pg-partman extension image to your Cluster

Add the image to a Cluster and preload the background worker:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-partman
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_partman_bgw
    extensions:
    - name: pg-partman
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_partman;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

For `pg_partman`, create the `partman` schema first and use
`CREATE EXTENSION pg_partman SCHEMA partman;`, or set `schema: partman` in the
declarative extension entry.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_partman
```

You should see `pg_partman` listed with its installed SQL version.

See the [pg_partman documentation](https://github.com/pgpartman/pg_partman/tree/development/doc)
for partition-set configuration examples.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
