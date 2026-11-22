# plsh

Lets you write PostgreSQL functions as shell scripts. Use it to call an
existing shell script from SQL and read back its output.

> [!CAUTION]
> PL/sh is an untrusted language with no trusted variant. Its functions can
> access files, run programs, and use the network as PostgreSQL’s
> operating-system user; reserve it for exceptional cases requiring that level
> of access.

Shell functions use the shell interpreter and command-line tools included in the
CNPG PostgreSQL base image.

For more information, see the [upstream documentation](https://github.com/petere/plsh).

### 1. Add the plsh extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-plsh
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: plsh
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION plsh;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT extversion FROM pg_extension WHERE extname = 'plsh';
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
