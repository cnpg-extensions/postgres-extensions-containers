# plproxy

database partitioning system for PostgreSQL 18. [Upstream documentation](https://plproxy.github.io/).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Usage

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

Connect to the database with `psql` and run `\dx` to check the installed extensions.

## Operation and privileges

PL/Proxy forwards SQL through PostgreSQL connections. Its dynamically linked libpq and transitive libraries are supplied by the matching CNPG minimal base (which includes psql); no runtime installation is needed. Configure connection strings and credentials through SQL and Kubernetes Secrets, and allow only required outbound destinations.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

ISC. Redistribution notices are preserved under `/licenses/`.

PL/Proxy CONNECT strings use libpq keyword/value syntax (for example, `host=cluster-rw dbname=app user=proxy_user`), not connection URIs: the plugin adds connection options to the string. Supply credentials through your deployment Secrets.
