# pg-statviz
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[`pg_statviz`](https://github.com/vyruss/pg_statviz) captures PostgreSQL statistics in database tables for later SQL analysis. The report generator and chart output are provided by a user-operated external client; this image adds no listener or web UI.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the extension image to a complete Cluster definition:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-statviz
spec:
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    extensions:
    - name: pg-statviz
~~~

Install the extension in the database:

~~~yaml
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
~~~

Create a snapshot and inspect its timestamp:

~~~sql
SELECT pgstatviz.snapshot();
SELECT * FROM pgstatviz.snapshots ORDER BY snapshot_tstamp DESC;
~~~

Snapshots are stored in ordinary database tables and included in database backups. Define SQL-based retention for the expected snapshot volume. `SELECT pgstatviz.delete_snapshots();` truncates the snapshot tables and is the packaged cleanup operation; it removes all snapshots. The image does not write report files.

## Supported matrix and licenses

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. The package's PostgreSQL-style license is included under `/licenses/postgresql-18-statviz/`. Renovate tracks the PGDG package.
