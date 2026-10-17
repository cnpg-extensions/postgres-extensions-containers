# pg_parquet
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_parquet](https://github.com/CrunchyData/pg_parquet) lets PostgreSQL read
and write Parquet files with `COPY TO` and `COPY FROM`, on the local
filesystem, S3, Azure Blob Storage, Google Cloud Storage and HTTP(S).

PGDG does not ship pg_parquet, so the image is built from the upstream release
tag with `cargo pgrx`. Images are built for `linux/amd64` and `linux/arm64`.

## Usage

### 1. Add the pg-parquet extension image to your Cluster

Define the `pg-parquet` extension under the `postgresql.extensions` section of
your `Cluster` resource. No preloading is needed. For example:

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
    extensions:
    - name: pg-parquet
      image:
        reference: ghcr.io/cnpg-extensions/pg-parquet:0.5.1-18-trixie
```

### 2. Enable the extension in a database

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
  - name: pg_parquet
    version: '0.5.1'
```

Alternatively, run `CREATE EXTENSION pg_parquet;` in `psql`.

### 3. Verify installation

```sql
\dx
COPY (SELECT 1 AS a) TO '/tmp/test.parquet' WITH (format 'parquet');
```

Object storage access is configured through the usual environment variables
and credential files (see upstream documentation). Reading and writing local
files requires membership in the `parquet_read_server`/`parquet_write_server`
roles, and object storage requires `parquet_object_store_read`/
`parquet_object_store_write`.

## Contributors

This extension is maintained by:

- Tobias Florek (@ibotty)

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg_parquet` extension
is bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
