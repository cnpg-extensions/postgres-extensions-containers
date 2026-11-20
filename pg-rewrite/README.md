# pg_rewrite

[pg_rewrite](https://github.com/cybertec-postgresql/pg_rewrite) lets you rewrite PostgreSQL tables with less locking.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/cybertec-postgresql/pg_rewrite).

### 1. Add the pg-rewrite extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-rewrite
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_rewrite
    parameters:
      wal_level: logical
      output_plugin_libraries: pgoutput,test_decoding,pg_rewrite
    extensions:
    - name: pg-rewrite
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_rewrite;` in the target database.

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
\dx pg_rewrite
```

You should see `pg_rewrite` listed with its installed SQL version.

## Operation and privileges

Table rewriting needs logical WAL and a free replication slot. Ensure sufficient CNPG data-volume space for both table copies and retained WAL. Remove the old table with SQL after verification; inspect and remove any abandoned inactive replication slots after a failed operation.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
