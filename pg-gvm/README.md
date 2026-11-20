# pg-gvm

pg-gvm adds Greenbone helper functions to PostgreSQL, including host-list
matching, regular-expression matching and iCalendar schedule calculations. It
supplies the SQL library only; it does not install or operate Greenbone
Vulnerability Manager services.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

[Upstream project](https://github.com/greenbone/pg-gvm).

## Usage

### 1. Add the pg-gvm extension image to your Cluster

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
\dx pg-gvm
```

You should see `pg-gvm` listed with its installed SQL version.

The image installs the pg-gvm SQL extension but not a GVM manager or scanner. A standalone expression check is:

~~~sql
SELECT regexp('host.example', '^host');
~~~

The package also includes host-list and iCalendar helpers used by Greenbone SQL workflows. `hosts_contains()` reads Greenbone's `meta` table, so it is exercised only in a database with that application schema installed.
