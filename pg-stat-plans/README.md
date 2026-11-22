# pg-stat-plans
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Tracks aggregate per-plan call counts, execution times, plan IDs, and `EXPLAIN`
plan text in PostgreSQL.
Use it to investigate whether a query became slower because PostgreSQL chose a
different way to run it.

For more information, see the [upstream documentation](https://github.com/pganalyze/pg_stat_plans).

### 1. Add the pg-stat-plans extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pg_stat_plans` in `shared_preload_libraries`, as
shown below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-plans
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_stat_plans
    extensions:
    - name: pg-stat-plans
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_stat_plans;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Inspect the collected plan statistics:

~~~sql
SELECT * FROM pg_stat_plans;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
