# pg_graphql
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pg_graphql adds GraphQL support to PostgreSQL. It reflects the SQL schema and
exposes it through the `graphql.resolve(...)` SQL function, so clients can query
the database with GraphQL without a separate application server.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/supabase/pg_graphql).

### 1. Add the pg-graphql extension image to your Cluster

Define the `pg-graphql` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-graphql
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-graphql
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_graphql;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_graphql
```

You should see `pg_graphql` listed with its installed SQL version.

## Known Caveats

GraphQL introspection is disabled by default from pg_graphql 1.6.0 onward. To
enable schema exploration tools for a schema, add the upstream directive, for
example:

```sql
COMMENT ON SCHEMA public IS e'@graphql({"introspection": true})';
```

See the [upstream configuration guide](https://supabase.github.io/pg_graphql/configuration/)
for the available schema directives.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
