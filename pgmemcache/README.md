# pgmemcache
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pgmemcache](https://github.com/ohmu/pgmemcache) is a PostgreSQL extension that provides an interface to Memcached from within SQL. It allows PostgreSQL to get, set, delete, and manage keys in a Memcached server directly using SQL functions.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

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
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pgmemcache
    parameters:
      pgmemcache.default_servers: memcached:11211
    extensions:
    - name: pgmemcache
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pgmemcache;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

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
