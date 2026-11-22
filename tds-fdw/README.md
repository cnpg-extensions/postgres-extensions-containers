# tds_fdw
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Enables PostgreSQL to query Microsoft SQL Server and Sybase databases using the
TDS (Tabular Data Stream) protocol via FreeTDS. Use it to combine PostgreSQL
records with data that still lives in a SQL Server database.

For more information, see the [upstream documentation](https://github.com/tds-fdw/tds_fdw).

### 1. Add the tds-fdw extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

Define the `tds-fdw` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-tds-fdw
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: tds-fdw
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION tds_fdw;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT tds_fdw_validator(ARRAY[]::text[], 'pg_foreign_server'::regclass);
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
