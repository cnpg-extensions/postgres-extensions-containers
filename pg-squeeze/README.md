# pg-squeeze
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

The requested pg-squeeze image contains the upstream
[pg_squeeze](https://github.com/cybertec-postgresql/pg_squeeze) extension. It
removes unused table space and can sort tuples according to an index while
allowing normal reads and writes for most of the operation.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the image to a Cluster. PostgreSQL 18 requires logical decoding for this
extension:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-squeeze
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
    parameters:
      max_replication_slots: '1'
      output_plugin_libraries: pg_squeeze
      wal_level: logical
    shared_preload_libraries:
    - pg_squeeze
    extensions:
    - name: pg-squeeze
~~~

Enable the SQL extension in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-squeeze-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-squeeze
  extensions:
  - name: pg_squeeze
~~~

The extension stores its configuration and logs in the squeeze schema. A
table can be registered for maintenance after it has an identity index:

~~~sql
CREATE EXTENSION pg_squeeze;
INSERT INTO squeeze.tables (tabschema, tabname, schedule)
VALUES ('public', 'my_table', ('{30}', '{22}', NULL, NULL, '{3, 5}'));
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-squeeze/.
