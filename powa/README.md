# PoWA server
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

PostgreSQL Workload Analyzer server-side history and snapshot schema. [Upstream project](https://powa.readthedocs.io/en/stable/).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the powa extension image to your Cluster

Create a dedicated PoWA Database and declare its required extensions:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-powa
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_stat_statements
    - powa
    extensions:
    - name: powa
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION powa;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

Install `pg_stat_statements`, then `btree_gist`, then `powa` in that order.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Install `pg_stat_statements` and `btree_gist` in that Database as well. Start the separate PoWA collector/archivist only after server-side snapshots are configured. Use `powa_take_snapshot()` for a manual one-shot snapshot.

## Package and runtime details

PG18 images use the PGDG `postgresql-18-powa` package. The image carries the `powa.so` server module, its PostgreSQL LLVM bitcode, SQL/control files, and the full Debian copyright notice under `/licenses/postgresql-18-powa/`. The module's only external runtime dependency is libc from the CNPG base image. PoWA requires the base-image `pg_stat_statements` and `btree_gist` extensions. Its background worker is provided by `powa.so`; a separate PoWA collector/archivist and web UI are optional client components.

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. Renovate tracks the PGDG package pins in `metadata.hcl`.
