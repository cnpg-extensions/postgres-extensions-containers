# plproxy

Lets you route function calls to remote PostgreSQL databases for partitioned
workloads. Use it to look up records spread across several databases without
having to choose the right database for each request.

PL/Proxy is an untrusted language with no trusted variant. Only database
superusers can create its functions, which can connect to other databases
using credentials available to PostgreSQL. Reserve function creation for
administrators who control those connections.

For more information, see the [upstream documentation](https://plproxy.github.io/).

### 1. Add the plproxy extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-plproxy
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: plproxy
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION plproxy;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT extversion FROM pg_extension WHERE extname = 'plproxy';
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
