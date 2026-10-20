# pg_parquet
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_parquet](https://github.com/CrunchyData/pg_parquet) is a PostgreSQL
extension for reading and writing [Parquet files](https://parquet.apache.org)
with PostgreSQL's `COPY TO/FROM` commands. It supports local files, S3, Azure
Blob Storage, Google Cloud Storage, and HTTP(S) endpoints. This image supports
PostgreSQL 18 on Debian bookworm and trixie.

## Usage

### 1. Add the pg-parquet extension image to your Cluster

Define the `pg-parquet` extension under the `postgresql.extensions` section of
your `Cluster` resource. The extension must also be added to
`shared_preload_libraries`. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-parquet
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
    - "pg_parquet"

    extensions:
    - name: pg-parquet
      image:
        reference: ghcr.io/cnpg-extensions/pg-parquet:v0.5.1-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_parquet` in a specific database by creating or updating a
`Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-parquet-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-parquet
  extensions:
  - name: pg-parquet
    version: '0.5.1'
```

Alternatively, enable it directly with SQL:

```sql
CREATE EXTENSION pg_parquet;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_parquet` listed with version `0.5.1`.

## Known Caveats

- `pg_parquet` must be loaded through `shared_preload_libraries`; the Cluster
  configuration above supplies this setting.
- To read from or write to an object store, grant the corresponding
  `parquet_object_store_read` or `parquet_object_store_write` role to the
  PostgreSQL user. Configure credentials using the methods described in the
  [upstream documentation](https://github.com/CrunchyData/pg_parquet#object-store-support).
- The `pg_parquet.enable_copy_hooks` parameter can be set to `off` to disable
  the extension's COPY hooks for a session or role.

## Contributors

This extension is maintained by:

- Jeremy Schneider ([@ardentperf](https://github.com/ardentperf))

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg_parquet` extension
and its dependencies is bundled within the image at:

```text
/licenses/
```

The extension itself is distributed under the [PostgreSQL
License](https://github.com/CrunchyData/pg_parquet/blob/v0.5.1/LICENSE).
By using this image, you agree to comply with the terms of the licenses
contained therein.
