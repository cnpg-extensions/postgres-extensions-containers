# pgmemcache
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pgmemcache](https://github.com/ohmu/pgmemcache) is a PostgreSQL extension that provides an interface to Memcached from within SQL. It allows PostgreSQL to get, set, delete, and manage keys in a Memcached server directly using SQL functions.

## Usage

### 1. Add the pgmemcache extension image to your Cluster

Define the `pgmemcache` extension under the `postgresql.extensions` section of
your `Cluster` resource. Note that `pgmemcache` must be added to
`shared_preload_libraries` to configure the Memcached connection at startup.
For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgmemcache
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
      - "pgmemcache"

    parameters:
      pgmemcache.default_servers: "memcached:11211"

    extensions:
    - name: pgmemcache
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pgmemcache
        reference: ghcr.io/cnpg-extensions/pgmemcache:2.3.0-18-trixie
```

### 2. Enable the extension in a database

You can install `pgmemcache` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgmemcache-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgmemcache
  extensions:
  - name: pgmemcache
    # renovate: suite=trixie-pgdg depName=postgresql-18-pgmemcache extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '2.3.0'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pgmemcache;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pgmemcache` listed among the installed extensions.

## Known Caveats

- **Requires a running Memcached server**: This extension connects to a
  Memcached server at startup (via `pgmemcache.default_servers`). Without a
  reachable Memcached server, PostgreSQL will log warnings but continue to
  start. Functions that access Memcached will fail if no server is configured.
- **`shared_preload_libraries` required**: `pgmemcache` must be in
  `shared_preload_libraries` to establish Memcached connections at PostgreSQL
  startup.
- **Runtime library dependency**: This extension requires `libmemcached11` at
  runtime. The library is bundled in the image under `/system/`.
- **Testing limitation**: The CI tests verify that the extension can be created
  (`CREATE EXTENSION pgmemcache`), but do not test actual Memcached
  connectivity. No Memcached server is provisioned in the test environment.
- **License**: `pgmemcache` is BSD-3-Clause, but its runtime dependency
  `libmemcached11` is LGPL, which is why this extension is hosted in the
  CNPG Extensions project rather than upstream.

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pgmemcache` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
