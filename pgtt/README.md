# pgtt

PostgreSQL Global Temporary Tables. [Upstream documentation](https://github.com/darold/pgtt/).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Declarative setup

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgtt
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
    parameters:
      session_preload_libraries: pgtt
    extensions:
    - name: pgtt
```

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgtt-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgtt
  extensions:
  - name: pgtt
```

## Operation and privileges

Global temporary table definitions are shared, while rows are session-local. Load `pgtt` for each session with the declarative parameter below. Temporary rows live in PostgreSQL-managed temporary storage and are removed at session end; ON COMMIT controls transaction cleanup.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

ISC. Redistribution notices are preserved under `/licenses/`.
Maintained by Jeremy Schneider (@ardentperf).
