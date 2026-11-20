# show-plans
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pg_show_plans shows the query plans of currently running PostgreSQL statements.
Plans can be returned as plain text, JSON, YAML, or XML.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the show-plans extension image to your Cluster

Add the image to a Cluster and preload pg_show_plans:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-show-plans
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_show_plans
    extensions:
    - name: show-plans
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_show_plans;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_show_plans
```

You should see `pg_show_plans` listed with its installed SQL version.

Inspect plans for currently running statements:

~~~sql
CREATE EXTENSION IF NOT EXISTS pg_show_plans;
SELECT * FROM pg_show_plans;
SELECT * FROM pg_show_plans_q;
~~~
