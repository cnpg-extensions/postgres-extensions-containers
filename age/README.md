# Apache AGE
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Apache AGE is a PostgreSQL extension that provides graph database functionality,
enabling you to store, query, and analyze graph data using Cypher queries
alongside SQL. It is based on the openCypher graph query language.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the age extension image to your Cluster

Define the `age` extension under the `postgresql.extensions` section of
your `Cluster` resource. Note that `age` must be added to
`shared_preload_libraries` for the extension to function. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-age
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - age
    extensions:
    - name: age
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION age;` in the target database.

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
\dx age
```

You should see `age` listed with its installed SQL version.

## Known Caveats

- **`shared_preload_libraries` required**: Apache AGE must be listed in
  `shared_preload_libraries`. Without it, `CREATE EXTENSION age` will fail
  with a "must be preloaded" error.
- **Cypher support**: After installation, use `SET search_path = ag_catalog, "$user", public;`
  to access AGE's graph functions and the `cypher()` function for graph queries.
