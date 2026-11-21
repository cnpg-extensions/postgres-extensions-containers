# pg-statviz
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Captures PostgreSQL statistics in database tables for later SQL analysis.
Use it to compare database activity before and during a slowdown.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/vyruss/pg_statviz).

The report generator and chart output are provided by a user-operated external
client; this image adds no listener or web UI.

### 1. Add the pg-statviz extension image to your Cluster

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
\dx pg_statviz
```

You should see `pg_statviz` listed with its installed SQL version.

Create a snapshot and inspect its timestamp:

~~~sql
SELECT pgstatviz.snapshot();
SELECT * FROM pgstatviz.snapshots ORDER BY snapshot_tstamp DESC;
~~~

Snapshots are stored in ordinary database tables and included in database backups. Define SQL-based retention for the expected snapshot volume. `SELECT pgstatviz.delete_snapshots();` truncates the snapshot tables and is the packaged cleanup operation; it removes all snapshots. The image does not write report files.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
