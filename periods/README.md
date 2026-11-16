# periods

PERIODs and SYSTEM VERSIONING for PostgreSQL. [Upstream documentation](https://github.com/xocolatl/periods).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Usage

### 1. Add the periods extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-periods
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: periods
```

### 2. Enable the extension in a database

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-periods-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-periods
  extensions:
  - name: btree_gist
  - name: periods
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

## Operation and privileges

Temporal history uses ordinary PostgreSQL tables on the CNPG data volume. To retire history, suspend system versioning with `periods.drop_system_versioning`, delete expired history rows using SQL, then re-enable versioning. Define your retention interval and execute maintenance through an external SQL scheduler.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

PostgreSQL. Redistribution notices are preserved under `/licenses/`.
