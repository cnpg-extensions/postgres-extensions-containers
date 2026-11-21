# PoWA server
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Records PostgreSQL workload statistics and snapshots so you can analyze
database activity over time. Use it to look back at which queries made your
database busy during a slowdown.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://powa.readthedocs.io/en/stable/).

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

Once the database is ready, connect to it with `psql` and run:

```sql
\dx powa
```

You should see `powa` listed with its installed SQL version.

Install `pg_stat_statements` and `btree_gist` in that database as well. The
preloaded background worker connects to a database named `powa` by default;
create that database and install all three extensions there, or configure
`powa.database` with your chosen database name in the Cluster parameters.
Start a separate PoWA collector or web UI only after server-side snapshots
are configured. Use `powa_take_snapshot()` for a manual one-shot snapshot.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
