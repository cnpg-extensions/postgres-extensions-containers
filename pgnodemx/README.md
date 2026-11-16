# pgnodemx

capture node OS metrics from PostgreSQL. [Upstream documentation](https://github.com/pgnodemx/pgnodemx).

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Declarative setup

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgnodemx
spec:
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    shared_preload_libraries:
    - pgnodemx
    parameters:
      pgnodemx.kdapi_enabled: 'off'
    extensions:
    - name: pgnodemx
```

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
Maintained by Jeremy Schneider (@ardentperf).
