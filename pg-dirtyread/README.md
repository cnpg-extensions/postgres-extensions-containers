# pg_dirtyread

Read dead but unvacuumed tuples from a PostgreSQL relation. [Upstream documentation](https://github.com/df7cb/pg_dirtyread).

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
  name: cluster-pg-dirtyread
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
    extensions:
    - name: pg-dirtyread
```

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-dirtyread-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-dirtyread
  extensions:
  - name: pg_dirtyread
```

## Operation and privileges

Superuser-only inspection can recover dead tuples that PostgreSQL has not vacuumed. It does not replace backups and may reveal data deleted by application users. The upstream regression test disables autovacuum only on its disposable test tables.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

BSD-3-Clause. Redistribution notices are preserved under `/licenses/`.
Maintained by Jeremy Schneider (@ardentperf).
