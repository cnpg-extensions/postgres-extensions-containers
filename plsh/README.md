# plsh

PL/sh lets you write PostgreSQL functions as shell scripts.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the plsh extension image to your Cluster

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
\dx plsh
```

You should see `plsh` listed with its installed SQL version.

## Operation and privileges

PL/sh is an untrusted language: only superusers can create its functions. Commands run as the PostgreSQL OS user and inherit its filesystem and network access. This image supports the `/bin/sh` already supplied by the matching CNPG minimal image, with shell built-ins only. It does not add arbitrary external commands or support file-producing functions. Restrict function EXECUTE grants to trusted administrators.
