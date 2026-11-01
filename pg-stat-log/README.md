# pg-stat-log
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[`pg_stat_log`](https://github.com/fabriziomello/pg_stat_log) collects cumulative counts of server log messages grouped by backend, database, role, severity, and SQLSTATE, with optional grouping by query identifier. It uses PostgreSQL 18's Custom Cumulative Stats API and must be preloaded. The PGDG package and SQL catalog versions are both `0.3`.

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
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-stat-log
        reference: ghcr.io/cnpg-extensions/pg-stat-log:0.3-18-trixie
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
    # SQL and Debian package versions are independently versioned.
    # SQL version must be checked in the package control files before merging updates.
    version: '0.3'
~~~

Inspect recent counts as a role with `pg_read_all_stats`:

~~~sql
SELECT database_name, user_name, elevel, sqlerrcode, count
FROM pg_stat_log
ORDER BY count DESC;
~~~

Statistics persist across clean PostgreSQL restarts and are discarded after crash recovery. Reset counters and reclaim tracked slots with `SELECT pg_stat_log_reset();`. Capacity is bounded by `pg_stat_log.max_entries` (default 1024); increase it and restart if `pg_stat_log_info().n_dropped` grows. The extension writes no external files.

## Upgrading from package 0.1 or 0.2

Both older packages install SQL version `0.1`. Follow the [upstream upgrade guidance](https://github.com/fabriziomello/pg_stat_log/blob/0.3/README.md#upgrading-from-01-or-02):

1. Before upgrading, save any statistics you need. The first server start with the `0.3` library resets **all PostgreSQL cumulative statistics**, because the persisted entry layout changed. Later clean restarts preserve counters as usual.
2. Update the extension image and restart PostgreSQL to load the new library.
3. Before updating the SQL objects, drop user-defined views that depend on `pg_stat_log` or `pg_stat_log_data()`. The upgrade recreates those objects, so recreate dependent views and reapply custom grants afterwards. The default grants to `pg_read_all_stats` are restored automatically.
4. Set the managed Database extension version to `'0.3'` in every database where it is installed. For installations managed directly through SQL, run `ALTER EXTENSION pg_stat_log UPDATE TO '0.3';` in each database instead.

The old SQL `0.1` view and function continue to work with the new library until the SQL upgrade, but do not expose `query_id`. Query identifier collection is optional and requires `pg_stat_log.compute_query_id = on` and PostgreSQL's `compute_query_id` enabled; see [upstream configuration](https://github.com/fabriziomello/pg_stat_log/blob/0.3/README.md#query-identifiers).

## Supported matrix and licenses

PGDG supplies this image for PostgreSQL 18 on Debian Bookworm and Trixie. The PostgreSQL license notice is included under `/licenses/postgresql-18-stat-log/`. Renovate follows the versioned PGDG package.
