# Mimeo
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Specialized per-table replication using snapshot, incremental, and DML-based methods. [Upstream project](https://pgxn.org/dist/mimeo/1.5.1/doc/mimeo.html).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

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

Connect to the database with `psql` and run `\dx` to check the installed extensions.

The `mimeo` control file requires `dblink`; install both extensions in the destination Database. By default, the PGDG SQL installs its objects in `public`, including `public.dblink_mapping_mimeo`, `public.table_maker`, and `public.refresh_table`. Store source credentials in the mapping table using appropriately restricted roles, and schedule refresh functions from a separate client. Mimeo copies selected tables, not a cluster or database catalog.

## Package and runtime details

PG18 images use the PGDG `postgresql-18-mimeo` package. Its full Debian copyright notice is carried in `/licenses/postgresql-18-mimeo/`. Requires the CNPG base-image `dblink` extension. Upstream recommends `pg_jobmon` for audit logging; it is optional.

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. Renovate tracks the PGDG package pins in `metadata.hcl`.

For this standalone setup, pass `p_jobmon := false` to `table_maker` and
`refresh_table`. Enable job logging only after separately provisioning the
optional `pg_jobmon` extension.
