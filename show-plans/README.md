# show-plans
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_show_plans](https://github.com/cybertec-postgresql/pg_show_plans) shows the
query plans of currently running PostgreSQL statements. Plans can be returned
as plain text, JSON, YAML, or XML.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the image to a Cluster and preload pg_show_plans:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-show-plans
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
    - pg_show_plans
    extensions:
    - name: show-plans
~~~

Enable the SQL extension in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-show-plans-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-show-plans
  extensions:
  - name: pg_show_plans
~~~

Inspect plans for currently running statements:

~~~sql
CREATE EXTENSION pg_show_plans;
SELECT * FROM pg_show_plans;
SELECT * FROM pg_show_plans_q;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-show-plans/.
