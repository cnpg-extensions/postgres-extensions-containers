# pg_track_settings

PostgreSQL extension tracking of configuration settings. [Upstream documentation](https://powa.readthedocs.io/).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Usage

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

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-track-settings-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-track-settings
  extensions:
  - name: pg_track_settings
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

## Operation and privileges

Snapshots and history are ordinary database tables. Schedule `pg_track_settings_snapshot()` through a SQL scheduler. `pg_track_settings_reset()` clears stored history; archive needed rows and set an explicit retention schedule before running it.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

PostgreSQL. Redistribution notices are preserved under `/licenses/`.
