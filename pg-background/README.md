# pg-background
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[`pg_background`](https://github.com/vibhorkum/pg_background) runs SQL in PostgreSQL background workers and returns completion metadata to the calling session. It does not require `shared_preload_libraries`; preloading is only needed if you want to set its GUCs in server configuration before first use.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

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

Connect to the database with `psql` and run `\dx` to check the installed extensions.

A superuser can run work asynchronously and check its result:

~~~sql
SELECT (pg_background_run('SELECT count(*) FROM pg_class')).*;
~~~

The command runs in a separate worker. Grant only the privileges needed by the SQL being run; background execution does not bypass PostgreSQL authorization.

## Supported matrix and licenses

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. Package copyright is included under `/licenses/postgresql-18-pg-background/`. PGDG package updates are tracked by Renovate.
