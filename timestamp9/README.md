# timestamp9
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds a timestamp type with nanosecond precision. Use it to keep very closely
timed events in order without losing their nanosecond timestamps.

For more information, see the [upstream documentation](https://github.com/optiver/timestamp9).

### 1. Add the timestamp9 extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-timestamp9
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: timestamp9
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION timestamp9;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

A SQL check that exercises the installed extension is:

```sql
SELECT '2026-09-29 00:00:00.000000001'::timestamp9 < '2026-09-29 00:00:00.000000002'::timestamp9;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
