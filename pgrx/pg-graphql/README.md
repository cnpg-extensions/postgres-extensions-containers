# pg_graphql
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds GraphQL support to PostgreSQL. Use it to fetch related records
together, such as a post and its author, with one GraphQL query.

For more information, see the [upstream documentation](https://github.com/supabase/pg_graphql).

### 1. Add the pg-graphql extension image to your Cluster

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

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

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT graphql.resolve('{ __typename }');
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
