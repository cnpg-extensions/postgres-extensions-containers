# pgtt

Provides global temporary tables with shared definitions and session-local
data. Use it to give each connection its own temporary workspace while
sharing the same table definition.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/darold/pgtt/).

### 1. Add the pgtt extension image to your Cluster

This example sets `session_preload_libraries: pgtt` to load the library for
each connection.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgtt
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      session_preload_libraries: pgtt
    extensions:
    - name: pgtt
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pgtt;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT count(*) AS global_temp_tables FROM pgtt_schema.pg_global_temp_tables;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
