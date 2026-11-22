# prioritize

Lets you inspect and change the operating system scheduling priority of
PostgreSQL backends. Use it to give a long report less CPU priority so more
urgent queries can take precedence.

> [!CAUTION]
> Lowering a backend’s CPU priority can delay other backends
> waiting for locks it holds, including internal spinlocks. Spinlock waits do
> not automatically raise the lock holder’s priority; exercise care and test
> under CPU contention before changing priorities in production. See the
> [PostgreSQL spinlock implementation](https://github.com/postgres/postgres/blob/master/src/backend/storage/lmgr/s_lock.c).

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/schmiddy/pg_prioritize).

### 1. Add the prioritize extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-prioritize
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: prioritize
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION prioritize;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT get_backend_priority(pg_backend_pid());
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
