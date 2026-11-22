# pg_rewrite

Lets you rewrite PostgreSQL tables with less locking. For example, change a
large table’s column types while keeping the table available for most of the
work.

For more information, see the [upstream documentation](https://github.com/cybertec-postgresql/pg_rewrite).

### 1. Add the pg-rewrite extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pg_rewrite` in `shared_preload_libraries`, as shown
below. Table rewriting also needs `wal_level: logical` and `pg_rewrite` in
`output_plugin_libraries`.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-rewrite
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_rewrite
    parameters:
      wal_level: logical
      output_plugin_libraries: pgoutput,test_decoding,pg_rewrite
    extensions:
    - name: pg-rewrite
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_rewrite;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT * FROM pg_rewrite_get_task_list();
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
