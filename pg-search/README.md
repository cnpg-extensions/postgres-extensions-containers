# pg_search
<!--
SPDX-FileCopyrightText: Copyright © contributors to the Not-CloudNativePG project.
SPDX-License-Identifier: Apache-2.0
-->

[pg_search](https://github.com/paradedb/paradedb) adds full-text search,
vector retrieval, filtering, and aggregations to PostgreSQL.

## Usage

### 1. Add the extension images to your Cluster

`pg_search` requires `pgvector`, so mount both extension images. It also links
system libraries supplied in the image's `system` directory.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-search
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    shared_preload_libraries:
    - "pg_search"
    extensions:
    - name: pg_search
      image:
        reference: ghcr.io/not-cloudnative-pg/pg-search:0.25.6-18-trixie
      ld_library_path:
      - system
    - name: pgvector
      image:
        reference: ghcr.io/cloudnative-pg/pgvector:0.8.6-18-trixie
```

### 2. Enable the extension in a database

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-search-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-search
  extensions:
  - name: vector
    version: '0.8.6'
  - name: pg_search
    version: '0.25.6'
```

Alternatively, enable both extensions directly with SQL:

```sql
CREATE EXTENSION vector;
CREATE EXTENSION pg_search;
```

### 3. Verify installation

Connect with `psql` and run `\dx`. Both `vector` and `pg_search` should be
listed among the installed extensions.

## Contributors

This extension is maintained by:

- Philippe Noël (@philippemnoel)

The maintainers are responsible for monitoring upstream releases and security
issues, ensuring compatibility with supported PostgreSQL versions, and
reviewing contributions to this extension image.

## Licenses and Copyright

The extension and dependency license notices are bundled under `/licenses/` in
the image.
