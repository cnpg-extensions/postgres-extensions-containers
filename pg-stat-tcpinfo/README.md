# pg_stat_tcpinfo
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Exposes live Linux TCP socket statistics through SQL so you can inspect
PostgreSQL connections.
Use it to check whether network delays explain a slow database connection.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/jakubwartakEDB/pg_stat_tcpinfo).

### 1. Add the pg-stat-tcpinfo extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-tcpinfo
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-stat-tcpinfo
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_stat_tcpinfo;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT pid, src_addr, src_port, dst_addr, dst_port, state,
       tcpinfo->>'rtt' AS rtt
FROM pg_stat_tcpinfo
WHERE state = 'ESTABLISHED'
ORDER BY pid;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
