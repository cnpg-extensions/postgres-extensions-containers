# pglogical

Replicates selected tables between PostgreSQL databases using logical
replication.
Use it to keep copies of selected tables up to date in another database.

This image includes `pglogical` for replication and `pglogical_origin`, an
empty compatibility extension for upgrades from PostgreSQL 9.4. Only `pglogical`
is needed for new installations; the example below enables both bundled extensions.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/2ndQuadrant/pglogical).

### 1. Add the pglogical extension image to your Cluster

This extension requires `pglogical` in `shared_preload_libraries`, as shown
below. Logical replication also needs `wal_level: logical` and
`pglogical_output` in `output_plugin_libraries`.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pglogical
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pglogical
    parameters:
      wal_level: logical
      output_plugin_libraries: pgoutput,test_decoding,pglogical_output
    extensions:
    - name: pglogical
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION pglogical;
CREATE EXTENSION pglogical_origin;
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
SELECT pglogical.pglogical_version();
SELECT extversion FROM pg_extension WHERE extname = 'pglogical_origin';
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
