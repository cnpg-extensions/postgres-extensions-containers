# pg-stat-plans
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_stat_plans](https://github.com/pganalyze/pg_stat_plans) tracks aggregate
per-plan call counts, execution times, plan IDs, and `EXPLAIN` plan text in
PostgreSQL. It is useful for identifying plan regressions and comparing
different plans chosen for the same query.

## Usage

Add the image to a Cluster and preload pg_stat_plans:

~~~yaml
postgresql:
  shared_preload_libraries:
  - pg_stat_plans
  extensions:
  - name: pg-stat-plans
    image:
      # renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-plans
      reference: ghcr.io/cnpg-extensions/pg-stat-plans:2.1.0-18-trixie
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
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-plans extractVersion=^(?<version>\d+\.\d+)
    version: '2.1'
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
