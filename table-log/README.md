# table_log

log changes on tables and restore tables to point in time. [Upstream documentation](https://github.com/df7cb/table_log).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Usage

### 1. Add the table-log extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-table-log
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: table-log
```

### 2. Enable the extension in a database

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-table-log-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-table-log
  extensions:
  - name: table_log
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

## Operation and privileges

Row-change audit records are ordinary database tables on the CNPG data volume. Protect log tables from application writes. Define retention and delete expired audit rows through SQL using the log timestamp column; normal VACUUM reclaims space. No external log file is used.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

LicenseRef-table-log. Redistribution notices are preserved under `/licenses/`.
