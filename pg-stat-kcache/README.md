# pg-stat-kcache
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_stat_kcache](https://github.com/powa-team/pg_stat_kcache) collects
per-query kernel statistics, including CPU time and filesystem reads and
writes. It uses the query identifiers supplied by the bundled
pg_stat_statements extension.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the image to a Cluster and preload both libraries:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-kcache
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
    - pg_stat_statements
    - pg_stat_kcache
    extensions:
    - name: pg-stat-kcache
~~~

Enable the SQL extension in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-stat-kcache-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-stat-kcache
  extensions:
  - name: pg_stat_statements
  - name: pg_stat_kcache
~~~

After running queries, inspect the collected values:

~~~sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_stat_kcache;
SELECT * FROM pg_stat_kcache;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-pg-stat-kcache/.
