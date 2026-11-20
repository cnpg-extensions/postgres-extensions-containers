# pg-stat-log
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_stat_log](https://github.com/fabriziomello/pg_stat_log) collects cumulative counts of server log messages grouped by
backend, database, role, severity, and SQLSTATE, with optional grouping by query
identifier. It must be preloaded.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/fabriziomello/pg_stat_log).

### 1. Add the pg-stat-log extension image to your Cluster

Add the image and preload its statistics worker in a complete Cluster definition:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-log
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_stat_log
    extensions:
    - name: pg-stat-log
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_stat_log;` in the target database.

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
\dx pg_stat_log
```

You should see `pg_stat_log` listed with its installed SQL version.

Inspect recent counts as a role with `pg_read_all_stats`:

~~~sql
SELECT database_name, user_name, elevel, sqlerrcode, count
FROM pg_stat_log
ORDER BY count DESC;
~~~

Statistics persist across clean PostgreSQL restarts and are discarded after crash recovery. Reset counters and reclaim tracked slots with `SELECT pg_stat_log_reset();`. Capacity is bounded by `pg_stat_log.max_entries` (default 1024); increase it and restart if the `n_dropped` value returned by `pg_stat_log_info()` grows. The extension writes no external files.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
