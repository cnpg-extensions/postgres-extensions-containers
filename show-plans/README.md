# show-plans
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Shows the query plans of currently running PostgreSQL statements. Use it to
investigate a slow query while it is still running.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/cybertec-postgresql/pg_show_plans).

### 1. Add the show-plans extension image to your Cluster

This extension requires `pg_show_plans` in `shared_preload_libraries`, as
shown below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-show-plans
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_show_plans
    extensions:
    - name: show-plans
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_show_plans;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Inspect plans for currently running statements:

~~~sql
CREATE EXTENSION IF NOT EXISTS pg_show_plans;
SELECT * FROM pg_show_plans;
SELECT * FROM pg_show_plans_q;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
