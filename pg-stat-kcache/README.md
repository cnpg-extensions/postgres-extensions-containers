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
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-stat-kcache extension image to your Cluster

Add the image to a Cluster and preload both libraries:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-kcache
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_stat_statements
    - pg_stat_kcache
    extensions:
    - name: pg-stat-kcache
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_stat_kcache;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

Install `pg_stat_statements`, then `pg_stat_kcache` in that order.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

After running queries, inspect the collected values:

~~~sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_stat_kcache;
SELECT * FROM pg_stat_kcache;
~~~

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-pg-stat-kcache/.
