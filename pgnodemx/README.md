# pgnodemx

Exposes host and container operating system metrics through PostgreSQL
functions. For example, check the database container’s memory use and limits
without logging into its host.

This image includes `pgnodemx` for reading system metrics and an optional
`pg_proctab` compatibility extension for tools such as `pg_top`. Enable
`pg_proctab` only if needed, using version `0.0.10-compat` after enabling
`pgnodemx`. In Kubernetes, these metrics describe the PostgreSQL container
and the resources visible to it, not necessarily the whole host.

For more information, see the [upstream documentation](https://github.com/pgnodemx/pgnodemx).

## Dependencies and conflicts

The optional `pg_proctab` compatibility extension requires `pgnodemx`
in the same database.

### 1. Add the pgnodemx extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pgnodemx` in `shared_preload_libraries`, as shown
below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgnodemx
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pgnodemx
    extensions:
    - name: pgnodemx
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION pgnodemx;
CREATE EXTENSION pg_proctab VERSION '0.0.10-compat';
```

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT pgnodemx_version();
SELECT * FROM pg_loadavg();
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
