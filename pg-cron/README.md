# pg_cron
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides a simple cron-based job scheduler for PostgreSQL, allowing you to
schedule PostgreSQL commands directly from the database. For example, delete
old records every night or refresh a report every hour.

For more information, see the [upstream documentation](https://github.com/citusdata/pg_cron).

### 1. Add the pg-cron extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pg_cron` in `shared_preload_libraries`, as shown
below. Set `cron.database_name` to the database where you install the
extension (`app` below). This example also enables
`cron.use_background_workers` to run jobs as background workers.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-cron
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      cron.database_name: app
      cron.use_background_workers: 'on'
    shared_preload_libraries:
    - pg_cron
    extensions:
    - name: pg-cron
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_cron;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT jobid, schedule, command FROM cron.job;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
