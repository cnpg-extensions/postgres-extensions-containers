# pg-gvm

pg-gvm adds Greenbone helper functions to PostgreSQL, including host-list matching, regular-expression matching and iCalendar schedule calculations. It supplies the SQL library only; it does not install or operate Greenbone Vulnerability Manager services.

The PGDG PG18 package is available on Trixie for amd64 and arm64. Bookworm has no PG18 package.

[Upstream project](https://github.com/greenbone/pg-gvm).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

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

Connect to the database with `psql` and run `\dx` to check the installed extensions.

The image installs the pg-gvm SQL extension but not a GVM manager or scanner. A standalone expression check is:

~~~sql
SELECT regexp('host.example', '^host');
~~~

The package also includes host-list and iCalendar helpers used by Greenbone SQL workflows. `hosts_contains()` reads Greenbone's `meta` table, so it is exercised only in a database with that application schema installed.

## Package, licensing and updates

PGDG package: 22.6.17-1.pgdg13+2; SQL version: 22.6. The extension is GPL-3.0-or-later and includes AGPL-3.0-or-later files. Copyright notices for the extension and bundled runtime packages are under `/licenses/<package>/`. The image includes no source archives.

Renovate tracks the PGDG package. Rebuild after package or base-image security updates and review the runtime libraries and notices.

The regex and calendar helpers work without a Greenbone application schema.
These helpers do not create files; the image adds no listener or background
service.

The runtime closure is dynamically linked. ICU and PCRE2 are redistributed under
their permissive notices; the GCC runtime libraries use the GCC Runtime Library
Exception. Copyright notices for bundled runtime packages are under
`/licenses/<package>/`. The matching CNPG base supplies glibc and the ELF loader.
