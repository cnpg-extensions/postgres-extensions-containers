# set_user

Lets you switch database roles with additional control and audit logging. Use
it to let an administrator perform maintenance under another role while
recording the role change.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/pgaudit/set_user).

### 1. Add the set-user extension image to your Cluster

This extension requires `set_user` in `shared_preload_libraries`, as shown
below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-set-user
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - set_user
    extensions:
    - name: set-user
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION set_user;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT extversion FROM pg_extension WHERE extname = 'set_user';
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
