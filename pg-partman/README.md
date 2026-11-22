# pg-partman
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Creates and maintains time-based and ID-based PostgreSQL partition sets. Use
it to split growing data into manageable tables and retire old data, such as
keeping only recent months of records.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/pgpartman/pg_partman).

### 1. Add the pg-partman extension image to your Cluster

To enable the optional maintenance worker, add `pg_partman_bgw` to
`shared_preload_libraries`. Set `pg_partman_bgw.dbname` and
`pg_partman_bgw.role` to the database and maintenance role (`app` below);
grant that role the privileges described in the upstream documentation.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-partman
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      pg_partman_bgw.dbname: app
      pg_partman_bgw.role: app
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

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
SELECT extversion FROM pg_extension WHERE extname = 'pg_partman';
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
