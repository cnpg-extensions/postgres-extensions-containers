# pg-qualstats
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Gathers statistics about predicates found in WHERE and JOIN clauses. Use it to
see which columns people filter on most when deciding where an index might
help.

For more information, see the [upstream documentation](https://github.com/powa-team/pg_qualstats).

### 1. Add the pg-qualstats extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pg_qualstats` in `shared_preload_libraries`, as
shown below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-qualstats
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_qualstats
    extensions:
    - name: pg-qualstats
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_qualstats;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Inspect the gathered predicate statistics with:

~~~sql
SELECT * FROM pg_qualstats;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
