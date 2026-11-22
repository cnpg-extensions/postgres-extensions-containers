# pgextwlist

Lets administrators allow non-superusers to install an approved selection of
PostgreSQL extensions.
Use it to let application teams enable approved extensions without giving them
full control of the server.

This image loads through `shared_preload_libraries`; it does not appear in
the database’s installed-extension list (`\dx` in `psql`).

For more information, see the [upstream documentation](https://github.com/dimitri/pgextwlist).

### 1. Add the pgextwlist extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pgextwlist` in `shared_preload_libraries`, as shown
below. Set `extwlist.extensions` to the extensions users may install; this
example allows `dblink`.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgextwlist
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pgextwlist
    parameters:
      extwlist.extensions: dblink
    extensions:
    - name: pgextwlist
```

### 2. Verify installation

Connect with `psql` and run `SHOW extwlist.extensions;` to check the configured
allowlist.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
