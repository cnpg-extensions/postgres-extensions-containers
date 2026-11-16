# pg-stat-log
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[`pg_stat_log`](https://github.com/fabriziomello/pg_stat_log) collects cumulative counts of server log messages grouped by backend, database, role, severity, and SQLSTATE, with optional grouping by query identifier. It uses PostgreSQL 18's Custom Cumulative Stats API and must be preloaded. The PGDG package and SQL catalog versions are both `0.3`.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the image and preload its statistics worker in a complete Cluster definition:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-log
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
    shared_preload_libraries:
    - pg_stat_log
    extensions:
    - name: pg-stat-log
~~~

Install the SQL view and functions in the database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-stat-log-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-stat-log
  extensions:
  - name: pg_stat_log
~~~

Inspect recent counts as a role with `pg_read_all_stats`:

~~~sql
SELECT database_name, user_name, elevel, sqlerrcode, count
FROM pg_stat_log
ORDER BY count DESC;
~~~

Statistics persist across clean PostgreSQL restarts and are discarded after crash recovery. Reset counters and reclaim tracked slots with `SELECT pg_stat_log_reset();`. Capacity is bounded by `pg_stat_log.max_entries` (default 1024); increase it and restart if `pg_stat_log_info().n_dropped` grows. The extension writes no external files.

## Supported matrix and licenses

PGDG supplies this image for PostgreSQL 18 on Debian Bookworm and Trixie. The PostgreSQL license notice is included under `/licenses/postgresql-18-stat-log/`. Renovate follows the versioned PGDG package.
