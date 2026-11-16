# pgextwlist

PostgreSQL Extension Whitelisting. [Upstream documentation](https://github.com/dimitri/pgextwlist).

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
  name: cluster-pgextwlist
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
    - pgextwlist
    parameters:
      extwlist.extensions: dblink
    extensions:
    - name: pgextwlist
```

## Operation and privileges

This module has no CREATE EXTENSION artifact. Its preload hook allows non-superusers to install administrator-allowlisted extensions that normally require superuser privileges; PostgreSQL trusted extensions retain their ordinary permissions. The example allowlists `dblink`, already present in the minimal PostgreSQL image. Optional custom script execution is not configured or supported by this image.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

PostgreSQL. Redistribution notices are preserved under `/licenses/`.
Maintained by Jeremy Schneider (@ardentperf).
