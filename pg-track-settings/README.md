# pg_track_settings

Records PostgreSQL configuration changes so you can review how settings have
changed over time.
Use it to check whether a changed database setting coincided with a slowdown.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://powa.readthedocs.io/en/stable/components/stats_extensions/pg_track_settings.html).

### 1. Add the pg-track-settings extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-track-settings
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-track-settings
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_track_settings;` in the target database.

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
\dx pg_track_settings
```

You should see `pg_track_settings` listed with its installed SQL version.

## Operation and privileges

Snapshots and history are ordinary database tables. Schedule `pg_track_settings_snapshot()` through a SQL scheduler. `pg_track_settings_reset()` clears stored history; archive needed rows and set an explicit retention schedule before running it.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
