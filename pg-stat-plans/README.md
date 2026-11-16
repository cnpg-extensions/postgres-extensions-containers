# pg-stat-plans
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_stat_plans](https://github.com/pganalyze/pg_stat_plans) tracks aggregate
per-plan call counts, execution times, plan IDs, and `EXPLAIN` plan text in
PostgreSQL. It is useful for identifying plan regressions and comparing
different plans chosen for the same query.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-stat-plans extension image to your Cluster

Add the image to a Cluster and preload pg_stat_plans:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-plans
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_stat_plans
    extensions:
    - name: pg-stat-plans
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_stat_plans;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Inspect the collected plan statistics:

~~~sql
SELECT * FROM pg_stat_plans;
~~~

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-pg-stat-plans/.
