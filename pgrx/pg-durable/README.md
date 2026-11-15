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
        # renovate: datasource=github-tags depName=microsoft/pg_durable versioning=semver depType=pgrx-source
        reference: ghcr.io/cnpg-extensions/pg-durable:0.2.9-18-trixie
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
  - name: pg_durable
    # renovate: datasource=github-tags depName=microsoft/pg_durable versioning=semver depType=pgrx-source
    version: '0.2.9'
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_durable;
```

### 3. Verify installation

The example installs the extension; worker database authentication also needs
configuration before application workflows can run (see [Known Caveats](#known-caveats)).

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

- Workers open separate database connections for management and for the
  submitting role. With CNPG's default local peer authentication, the worker
  running as the PostgreSQL OS user cannot authenticate as `app`; granting
  `df.grant_usage` alone does not resolve this. The upstream
  [connection host setting](https://github.com/microsoft/pg_durable/blob/v0.2.9/USER_GUIDE.md#connection-host)
  selects the connection endpoint, but authentication must work for both the
  management role (`postgres` by default) and submitting roles. In the tested
  CNPG 1.30.1 / PostgreSQL 18.7 setup, switching to TCP while allowing only
  `app` left management initialization failing authentication as `postgres`.
  A workflow completed with `pg_durable.host=127.0.0.1` and a disposable,
  loopback-only trust rule for both roles. This does not validate a production
  authentication configuration: a credential-based setup remains unverified,
  and the test's trust rule is not a production recommendation.

## Contributors

Maintained by Jeremy Schneider (@ardentperf).

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
