# hypopg
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides hypothetical indexes for PostgreSQL. Use it to check whether
PostgreSQL would choose a proposed index before spending time and disk space
building it.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/HypoPG/hypopg).

### 1. Add the hypopg extension image to your Cluster

Add the image to a Cluster:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-hypopg
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: hypopg
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION hypopg;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

For an existing table `my_table` with an integer `column_name` column, create a
hypothetical index and inspect the resulting plan in the same session:

~~~sql
SELECT * FROM hypopg_create_index('CREATE INDEX ON my_table (column_name)');
EXPLAIN SELECT * FROM my_table WHERE column_name = 1;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
