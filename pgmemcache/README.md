# pgmemcache
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides an interface to Memcached from within SQL. For example, clear a
cached value when the corresponding database record changes.

Run Memcached separately and make it reachable from your CNPG database.
This image supplies the PostgreSQL extension, not the Memcached server.

For more information, see the [upstream documentation](https://github.com/ohmu/pgmemcache).

### 1. Add the pgmemcache extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For the startup configuration shown below, add `pgmemcache` to
`shared_preload_libraries` and set `pgmemcache.default_servers` to your
Memcached endpoint.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgmemcache
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pgmemcache
    parameters:
      pgmemcache.default_servers: memcached:11211
    extensions:
    - name: pgmemcache
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pgmemcache;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT extversion FROM pg_extension WHERE extname = 'pgmemcache';
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
