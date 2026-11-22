# pg-hint-plan
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds optimizer hints to PostgreSQL. Use it to try a different way of running a
slow query, such as choosing a particular index. Hints are written in SQL
comments and can choose scan methods, join methods, and other planner behavior
for individual queries.

For more information, see the [upstream documentation](https://github.com/ossc-db/pg_hint_plan).

### 1. Add the pg-hint-plan extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This example adds `pg_hint_plan` to `shared_preload_libraries` to enable
hints globally.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-hint-plan
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_hint_plan
    extensions:
    - name: pg-hint-plan
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_hint_plan;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

The extension creates its objects in the hint_plan schema. For example:

~~~sql
CREATE TABLE hint_example (id integer PRIMARY KEY);
INSERT INTO hint_example SELECT generate_series(1, 1000);
ANALYZE hint_example;
/*+ SeqScan(t) */ EXPLAIN SELECT * FROM hint_example AS t WHERE id = 1;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
