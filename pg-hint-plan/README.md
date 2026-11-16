# pg-hint-plan
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_hint_plan](https://github.com/ossc-db/pg_hint_plan) adds optimizer hints
to PostgreSQL. Hints are written in SQL comments and can choose scan methods,
join methods, and other planner behavior for individual queries.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the image to a Cluster and preload pg_hint_plan:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-hint-plan
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
    - pg_hint_plan
    extensions:
    - name: pg-hint-plan
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
