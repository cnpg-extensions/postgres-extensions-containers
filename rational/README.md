# rational
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides exact integer-fraction arithmetic in PostgreSQL. Use it to calculate
with fractions such as one third without rounding them to decimals.

For more information, see the [upstream documentation](https://github.com/begriffs/pg_rational).

### 1. Add the rational extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-rational
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: rational
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_rational;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

A SQL check that exercises the installed extension is:

```sql
SELECT '1/2'::rational + '1/3'::rational = '5/6'::rational;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
