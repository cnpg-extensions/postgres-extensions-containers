# pg-gvm

Provides database helper functions for Greenbone vulnerability management.
Use it to support a Greenbone manager that stores scan results in PostgreSQL.

Run the Greenbone manager and scanners on a separate server. The manager
connects to your CNPG database; this image supplies only the database extension.

For more information, see the [upstream documentation](https://github.com/greenbone/pg-gvm).

### 1. Add the pg-gvm extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-gvm
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-gvm
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION "pg-gvm";` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Run a simple check of a helper function:

~~~sql
SELECT regexp('host.example', '^host');
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
