# plproxy

database partitioning system for PostgreSQL 18. [Upstream documentation](https://plproxy.github.io/).

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
  name: cluster-plproxy
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
    - name: plproxy
```

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-plproxy-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-plproxy
  extensions:
  - name: plproxy
```

## Operation and privileges

PL/Proxy forwards SQL through PostgreSQL connections. Its dynamically linked libpq and transitive libraries are supplied by the matching CNPG minimal base (which includes psql); no runtime installation is needed. Configure connection strings and credentials through SQL and Kubernetes Secrets, and allow only required outbound destinations.

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

PL/Proxy CONNECT strings use libpq keyword/value syntax (for example, `host=cluster-rw dbname=app user=proxy_user`), not connection URIs: the plugin adds connection options to the string. Supply credentials through your deployment Secrets.
