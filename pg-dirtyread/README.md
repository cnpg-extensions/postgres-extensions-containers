# pg_dirtyread

Lets you inspect dead rows that have not yet been removed by VACUUM. Use it to
inspect accidentally deleted records while their old contents are still on
disk.

For more information, see the [upstream documentation](https://github.com/df7cb/pg_dirtyread).

### 1. Add the pg-dirtyread extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-dirtyread
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-dirtyread
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_dirtyread;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT extversion FROM pg_extension WHERE extname = 'pg_dirtyread';
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
