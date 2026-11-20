# Mimeo
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Mimeo replicates individual tables between PostgreSQL databases using snapshot,
incremental, and DML-based methods.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the mimeo extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-mimeo
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: mimeo
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION mimeo;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

Install `dblink`, then `mimeo` in that order.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx mimeo
```

You should see `mimeo` listed with its installed SQL version.

The `mimeo` control file requires `dblink`; install both extensions in the destination Database. By default, the PGDG SQL installs its objects in `public`, including `public.dblink_mapping_mimeo`, `public.table_maker`, and `public.refresh_table`. Store source credentials in the mapping table using appropriately restricted roles, and schedule refresh functions from a separate client. Mimeo copies selected tables, not a cluster or database catalog.

For this standalone setup, pass `p_jobmon := false` to `table_maker` and
`refresh_table`. Enable job logging only after separately provisioning the
optional `pg_jobmon` extension.
