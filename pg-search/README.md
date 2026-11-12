# pg_search
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_search](https://github.com/paradedb/paradedb) is a
PostgreSQL extension for fast full-text, faceted, and hybrid search over
PostgreSQL tables using the BM25 algorithm and Tantivy. This image supports
PostgreSQL 18 on Debian bookworm and trixie.

## Usage

### 1. Add the pg-search extension image to your Cluster

Define the `pg-search` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

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
    - name: pg-search
      image:
        reference: ghcr.io/cnpg-extensions/pg-search:0.26.6-18-trixie
```

`pg_search` also requires the `vector` extension. Make the `pgvector` image
available to the Cluster alongside this image.

### 2. Enable the extension in a database

You can install `pg_search` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For
example, to enable it in the `app` database:

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
  - name: pg_search
    version: '0.26.6'
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_search CASCADE;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_search
```

You should see `pg_search` listed with version `0.26.6`. The extension must be
included in `shared_preload_libraries`; the Cluster example above supplies this
setting, matching the image's catalog metadata.

## Known Caveats

- `pg_search` requires `vector` from [pgvector](https://github.com/pgvector/pgvector).
  Install or mount pgvector before creating `pg_search`.

## Contributors

Maintained by Jeremy Schneider (@ardentperf).

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
