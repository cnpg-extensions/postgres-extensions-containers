# pglogical

pglogical replicates selected tables between PostgreSQL databases using logical
replication.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/2ndQuadrant/pglogical).

### 1. Add the pglogical extension image to your Cluster

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

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pglogical;` in the target database.

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
\dx pglogical
```

You should see `pglogical` listed with its installed SQL version.

## Operation and privileges

Create provider and subscriber databases with this extension and matching table
definitions. Both endpoints must use CNPG-managed PostgreSQL Services. Store
connection credentials in Kubernetes Secrets and initialize nodes/subscriptions
from a declarative Job or your deployment system. Administrative setup and
replication roles need the privileges required by pglogical.

Call `pglogical.create_node` for each endpoint, register tables with
`pglogical.replication_set_add_table`, and call `pglogical.create_subscription`
on the subscriber. Set `synchronize_structure := false`. Optional schema
synchronization is unsupported until its temporary-file storage, access,
retention and cleanup are designed. Apply schema changes through your normal
migration process.

Monitor replication lag and retained WAL on the PostgreSQL data volume. Plan
slot limits and disk capacity; remove unused subscriptions with
`pglogical.drop_subscription` and remove unused nodes after their consumers are
stopped. Failed consumers must not retain WAL indefinitely. No extra listener
or container shell setup is required.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
