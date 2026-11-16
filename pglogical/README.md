# pglogical

Logical replication through PostgreSQL connections. [Upstream project](https://github.com/2ndQuadrant/pglogical).

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
  name: cluster-pglogical
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
    - pglogical
    parameters:
      wal_level: logical
      output_plugin_libraries: pgoutput,test_decoding,pglogical_output
    extensions:
    - name: pglogical
```

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pglogical-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pglogical
  extensions:
  - name: pglogical
```

## Operation and privileges

Create provider and subscriber databases with this extension and matching table
definitions. Both endpoints must use CNPG-managed PostgreSQL Services. Store
connection credentials in Kubernetes Secrets and initialize nodes/subscriptions
from a declarative Job or your deployment system. Administrative setup and
replication roles need the privileges required by pglogical.

Call `pglogical.create_node` for each endpoint, register tables with
`pglogical.replication_set_add_table`, and call `pglogical.create_subscription`
on the subscriber. Set `synchronize_structure := false`. Optional schema
synchronization is unsupported until its temporary-file storage, access,
retention and cleanup are designed. Apply schema changes through your normal
migration process.

Monitor replication lag and retained WAL on the PostgreSQL data volume. Plan
slot limits and disk capacity; remove unused subscriptions with
`pglogical.drop_subscription` and remove unused nodes after their consumers are
stopped. Failed consumers must not retain WAL indefinitely. No extra listener
or container shell setup is required.

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

The package also includes `pglogical_origin` version 1.0.0, an empty compatibility extension for upgrades from PostgreSQL 9.4. It is not needed for new PostgreSQL 18 replication setups. The upstream SQL suite exercises it in selected replication cases.
