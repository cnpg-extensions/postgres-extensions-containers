# plproxy

[PL/Proxy](https://plproxy.github.io/) lets you route function calls to remote PostgreSQL databases for
partitioned workloads.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://plproxy.github.io/).

### 1. Add the plproxy extension image to your Cluster

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

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx plproxy
```

You should see `plproxy` listed with its installed SQL version.

## Operation and privileges

PL/Proxy forwards SQL through PostgreSQL connections. Its dynamically linked libpq and transitive libraries are supplied by the matching CNPG minimal base (which includes psql); no runtime installation is needed. Configure connection strings and credentials through SQL and Kubernetes Secrets, and allow only required outbound destinations.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
