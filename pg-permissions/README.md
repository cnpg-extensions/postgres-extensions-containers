# pg_permissions

Lets you inspect database permissions through SQL views. Use it to check who
can read or change a table and spot access that should not be allowed.

For more information, see the [upstream documentation](https://github.com/cybertec-postgresql/pg_permissions).

### 1. Add the pg-permissions extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-permissions
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-permissions
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_permissions;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT * FROM table_permissions LIMIT 5;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
