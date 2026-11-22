# PoWA server
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Records PostgreSQL workload statistics and snapshots so you can analyze
database activity over time. Use it to look back at which queries made your
database busy during a slowdown.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

## Dependencies and conflicts

Requires `pg_stat_statements` and `btree_gist` in the same database.

For more information, see the [upstream documentation](https://powa.readthedocs.io/en/stable/).

### 1. Add the powa extension image to your Cluster

This extension requires `pg_stat_statements` and `powa` in
`shared_preload_libraries`, as shown below.

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

Create a database named `powa`, where the background worker connects by
default, and run the following SQL there. To use another database, set
`powa.database` in the Cluster parameters to its name.

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION powa;
```

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT id, hostname, port, dbname FROM powa_servers;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
