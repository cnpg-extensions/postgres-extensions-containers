# pg-squeeze
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Reclaims unused table space and can sort rows according to an index while
allowing normal reads and writes for most of the operation.
Use it to automatically shrink tables that have grown wasteful after many
updates and deletions.

For more information, see the [upstream documentation](https://github.com/cybertec-postgresql/pg_squeeze).

### 1. Add the pg-squeeze extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pg_squeeze` in `shared_preload_libraries`, as shown
below. Also set `wal_level: logical` and include `pg_squeeze` in
`output_plugin_libraries`.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-squeeze
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      output_plugin_libraries: pg_squeeze
      wal_level: logical
    shared_preload_libraries:
    - pg_squeeze
    extensions:
    - name: pg-squeeze
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_squeeze;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

The extension stores its configuration and logs in the squeeze schema. A
table can be registered for maintenance after it has an identity index. Replace
`public.my_table` with an existing table:

~~~sql
INSERT INTO squeeze.tables (tabschema, tabname, schedule)
VALUES ('public', 'my_table', ('{30}', '{22}', NULL, NULL, '{3, 5}'));
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
