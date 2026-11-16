# pgnodemx

capture node OS metrics from PostgreSQL. [Upstream documentation](https://github.com/pgnodemx/pgnodemx).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Usage

### 1. Add the pgnodemx extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgnodemx
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pgnodemx
    parameters:
      pgnodemx.kdapi_enabled: 'off'
    extensions:
    - name: pgnodemx
```

### 2. Enable the extension in a database

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgnodemx-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgnodemx
  extensions:
  - name: pgnodemx
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

## Operation and privileges

OS metrics reflect the container namespace and delegated cgroups, not necessarily the host. SQL functions require appropriate administrative privileges. Downward API functions are disabled in this example because no pod-info volume is supplied. Cgroup functions depend on available controllers; `/proc` metrics remain useful independently.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

PostgreSQL, Apache-2.0. Redistribution notices are preserved under `/licenses/`.
