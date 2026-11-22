# pg-statviz
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Saves snapshots of PostgreSQL activity for charts and reports.
Use it to compare how your database was behaving before and during a slowdown.

This image provides the database part of pg_statviz. Run its reporting tool
on a separate server and connect it to your CNPG database to create charts
and reports.

For more information, see the [upstream documentation](https://github.com/vyruss/pg_statviz).

### 1. Add the pg-statviz extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

Add the extension image to a complete Cluster definition:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-statviz
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-statviz
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_statviz;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Create a snapshot and inspect its timestamp:

~~~sql
SELECT pgstatviz.snapshot();
SELECT * FROM pgstatviz.snapshots ORDER BY snapshot_tstamp DESC;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
