# pg_durable
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_durable](https://github.com/microsoft/pg_durable) is a PostgreSQL extension
for durable, fault-tolerant SQL workflows. It checkpoints composable SQL steps
in PostgreSQL so executions can resume after crashes, restarts, or failed
steps, without an external orchestration service. This image supports
PostgreSQL 18 on Debian bookworm and trixie.

## Usage

### 1. Add the pg-durable extension image to your Cluster

Define the `pg-durable` extension under the `postgresql.extensions`
section of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-durable
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    parameters:
      pg_durable.database: "app"
    shared_preload_libraries:
    - "pg_durable"

    extensions:
    - name: pg-durable
      image:
        reference: ghcr.io/cnpg-extensions/pg-durable:v0.2.7-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_durable` in a specific database by creating or
updating a `Database` resource, or by running `CREATE EXTENSION` directly in
`psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-durable-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-durable
  extensions:
  - name: pg-durable
    version: '0.2.7'
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_durable;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_durable` listed among the installed extensions.

## Known Caveats

- `pg_durable` must be loaded through `shared_preload_libraries`, and its
  background worker processes the database named by `pg_durable.database`. The
  metadata and example above configure that database as `app`; create the
  extension there.
- `CREATE EXTENSION pg_durable` does not grant privileges to `PUBLIC`. Grant
  access to application roles with `SELECT df.grant_usage('app_role')` after
  creating the extension. Superuser-submitted workflows are disabled by
  default; enable them only when explicitly required.

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

All relevant license and copyright information for the `pg_durable`
extension and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
