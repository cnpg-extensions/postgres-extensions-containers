# pg-hint-plan
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_hint_plan](https://github.com/ossc-db/pg_hint_plan) adds optimizer hints
to PostgreSQL. Hints are written in SQL comments and can choose scan methods,
join methods, and other planner behavior for individual queries.

## Usage

Add the image to a Cluster and preload pg_hint_plan:

~~~yaml
postgresql:
  shared_preload_libraries:
  - pg_hint_plan
  extensions:
  - name: pg-hint-plan
    image:
      # renovate: suite=trixie-pgdg depName=postgresql-18-pg-hint-plan
      reference: ghcr.io/cnpg-extensions/pg-hint-plan:1.8.1-18-trixie
~~~

Enable the SQL extension in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-hint-plan-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-hint-plan
  extensions:
  - name: pg_hint_plan
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg-hint-plan extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '1.8.1'
~~~

The extension creates its objects in the hint_plan schema. For example:

~~~sql
CREATE EXTENSION pg_hint_plan;
/*+ SeqScan(t) */ EXPLAIN SELECT * FROM t WHERE id = 1;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-pg-hint-plan/.
