# pg-statviz
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[`pg_statviz`](https://github.com/vyruss/pg_statviz) captures PostgreSQL statistics in database tables for later SQL analysis. The report generator and chart output are provided by a user-operated external client; this image adds no listener or web UI.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

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

Install the extension in the database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-statviz-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-statviz
  extensions:
  - name: pg_statviz
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Create a snapshot and inspect its timestamp:

~~~sql
SELECT pgstatviz.snapshot();
SELECT * FROM pgstatviz.snapshots ORDER BY snapshot_tstamp DESC;
~~~

Snapshots are stored in ordinary database tables and included in database backups. Define SQL-based retention for the expected snapshot volume. `SELECT pgstatviz.delete_snapshots();` truncates the snapshot tables and is the packaged cleanup operation; it removes all snapshots. The image does not write report files.

## Supported matrix and licenses

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. The package's PostgreSQL-style license is included under `/licenses/postgresql-18-statviz/`. Renovate tracks the PGDG package.
