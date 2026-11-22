# extra-window-functions
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds window functions such as lag_ignore_nulls and lead_ignore_nulls. Use it to
compare a value with earlier or later values in a list, skipping missing ones.

For more information, see the [upstream documentation](https://github.com/xocolatl/extra_window_functions).

### 1. Add the extra-window-functions extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-extra-window-functions
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: extra-window-functions
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION extra_window_functions;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

A SQL check that exercises the installed extension is:

```sql
SELECT (SELECT lag_value = 10 FROM (SELECT i, lag_ignore_nulls(v) OVER (ORDER BY i) AS lag_value FROM (VALUES (1,10),(2,NULL),(3,20)) AS s(i,v)) AS windowed WHERE i=3);
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
