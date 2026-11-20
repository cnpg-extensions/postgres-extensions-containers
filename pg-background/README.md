# pg-background
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_background](https://github.com/vibhorkum/pg_background) runs SQL in PostgreSQL background workers and returns completion
metadata to the calling session. It does not require `shared_preload_libraries`;
preloading is only needed if you want to set its GUCs in server configuration
before first use.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/vibhorkum/pg_background).

### 1. Add the pg-background extension image to your Cluster

Add the extension image to a complete Cluster definition:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-background
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-background
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_background;` in the target database.

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
\dx pg_background
```

You should see `pg_background` listed with its installed SQL version.

A superuser can run SQL in a background worker and inspect its completion metadata:

~~~sql
SELECT * FROM pg_background_run('SELECT count(*) FROM pg_class');
~~~

Use the function in `FROM` so it executes once. Expanding
`(pg_background_run(...)).*` in the select list can execute it once per output
column. The command runs in a separate worker. Grant only the privileges needed by the SQL being run; background execution does not bypass PostgreSQL authorization.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
