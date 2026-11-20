# pgsentinel
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pgsentinel samples active session history into an in-memory ring buffer and
links session activity with pg_stat_statements.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the pgsentinel extension image to your Cluster

Add the image to a Cluster and preload both libraries:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgsentinel
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      pgsentinel.db_name: app
    shared_preload_libraries:
    - pg_stat_statements
    - pgsentinel
    extensions:
    - name: pgsentinel
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pgsentinel;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

The worker connects to `pgsentinel.db_name` (default `postgres`). Install
`pgsentinel` in that database; this example selects CNPG's application database
`app`. If the worker's database does not contain the extension, its history
remains empty even when queries run elsewhere in the cluster.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pgsentinel
```

You should see `pgsentinel` listed with its installed SQL version.

After the cluster has run for a few seconds, inspect the active session
history:

~~~sql
CREATE EXTENSION IF NOT EXISTS pgsentinel;
SELECT * FROM pg_active_session_history LIMIT 5;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
