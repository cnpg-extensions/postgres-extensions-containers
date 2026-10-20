# pg_graphql
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_graphql](https://github.com/supabase/pg_graphql) adds GraphQL support to
PostgreSQL. It reflects the SQL schema and exposes it through the
`graphql.resolve(...)` SQL function, so clients can query the database with
GraphQL without a separate application server. This image supports PostgreSQL
18 on Debian bookworm and trixie.

## Usage

### 1. Add the pg-graphql extension image to your Cluster

Define the `pg-graphql` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-graphql
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg-graphql
      image:
        reference: ghcr.io/cnpg-extensions/pg-graphql:v1.6.2-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_graphql` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For
example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-graphql-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-graphql
  extensions:
  - name: pg-graphql
    version: '1.6.2'
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_graphql;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_graphql` listed among the installed extensions.

## Known Caveats

GraphQL introspection is disabled by default from pg_graphql 1.6.0 onward. To
enable schema exploration tools for a schema, add the upstream directive, for
example:

```sql
COMMENT ON SCHEMA public IS e'@graphql({"introspection": true})';
```

See the [upstream configuration guide](https://supabase.github.io/pg_graphql/configuration/)
for the available schema directives.

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg_graphql` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
