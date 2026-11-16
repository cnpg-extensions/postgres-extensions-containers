# pg-stat-plans
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_stat_plans](https://github.com/pganalyze/pg_stat_plans) tracks aggregate
per-plan call counts, execution times, plan IDs, and `EXPLAIN` plan text in
PostgreSQL. It is useful for identifying plan regressions and comparing
different plans chosen for the same query.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the image to a Cluster and preload pg_stat_plans:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-plans
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
    - pg_stat_plans
    extensions:
    - name: pg-stat-plans
~~~

Enable the SQL extension in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-stat-plans-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-stat-plans
  extensions:
  - name: pg_stat_plans
~~~

Inspect the collected plan statistics:

~~~sql
CREATE EXTENSION pg_stat_plans;
SELECT * FROM pg_stat_plans;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-pg-stat-plans/.
