# hypopg
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[HypoPG](https://github.com/HypoPG/hypopg) provides hypothetical indexes for
PostgreSQL. It lets you compare query plans with an index that has not been
physically created.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the image to a Cluster:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-hypopg
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
    - name: hypopg
~~~

Enable the SQL extension in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-hypopg-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-hypopg
  extensions:
  - name: hypopg
~~~

Create a hypothetical index and inspect the resulting plan:

~~~sql
CREATE EXTENSION hypopg;
SELECT * FROM hypopg_create_index('CREATE INDEX ON my_table (column_name)');
EXPLAIN SELECT * FROM my_table WHERE column_name = 1;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-hypopg/.
