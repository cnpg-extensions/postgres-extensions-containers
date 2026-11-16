# pg-repack
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[`pg_repack`](https://github.com/reorg/pg_repack) rebuilds tables and indexes while allowing normal reads and writes. The server image provides the PostgreSQL extension library and SQL objects. The `pg_repack` client is run separately and must match the server's PostgreSQL major and extension version.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-repack extension image to your Cluster

Add the server image to a complete Cluster definition:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-repack
spec:
  imageCatalogRef: ...
  enableSuperuserAccess: true
  postgresql:
    extensions:
    - name: pg-repack
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_repack;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Run a matching client from a separate job, host, or maintenance image. On a Debian Trixie PostgreSQL 18 client, install the PGDG `postgresql-18-repack` package and connect through the Cluster's managed `-rw` service:

~~~sh
pg_repack --host=cluster-pg-repack-rw --username=postgres --dbname=app --table=public.large_table
~~~

Supply credentials through a Kubernetes Secret or the client environment. The extension image deliberately does not put the client executable in the PostgreSQL server image.

## Supported matrix and licenses

The server image supports PostgreSQL 18 on Debian Bookworm and Trixie. Package copyright (BSD-3-Clause) is included under `/licenses/postgresql-18-repack/`. The separate client must use the same upstream version; Renovate tracks PGDG package versions.
