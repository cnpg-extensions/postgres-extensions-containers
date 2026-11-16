# pg-squeeze
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

The requested pg-squeeze image contains the upstream
[pg_squeeze](https://github.com/cybertec-postgresql/pg_squeeze) extension. It
removes unused table space and can sort tuples according to an index while
allowing normal reads and writes for most of the operation.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-squeeze extension image to your Cluster

Add the image to a Cluster. PostgreSQL 18 requires logical decoding for this
extension:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-squeeze
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      max_replication_slots: '1'
      output_plugin_libraries: pg_squeeze
      wal_level: logical
    shared_preload_libraries:
    - pg_squeeze
    extensions:
    - name: pg-squeeze
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_squeeze;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

The extension stores its configuration and logs in the squeeze schema. A
table can be registered for maintenance after it has an identity index. Replace
`public.my_table` with an existing table:

~~~sql
INSERT INTO squeeze.tables (tabschema, tabname, schedule)
VALUES ('public', 'my_table', ('{30}', '{22}', NULL, NULL, '{3, 5}'));
~~~

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-squeeze/.
