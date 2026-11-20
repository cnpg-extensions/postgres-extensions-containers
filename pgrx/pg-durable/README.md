# pg_durable
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pg_durable is a PostgreSQL extension for durable, fault-tolerant SQL workflows.
It checkpoints composable SQL steps in PostgreSQL so executions can resume after
crashes, restarts, or failed steps, without an external orchestration service.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/microsoft/pg_durable).

### 1. Add the pg-durable extension image to your Cluster

Define the `pg-durable` extension under the `postgresql.extensions`
section of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-durable
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      pg_durable.database: app
    shared_preload_libraries:
    - pg_durable
    extensions:
    - name: pg-durable
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_durable;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

The example installs the extension; worker database authentication also needs
configuration before application workflows can run (see [Known Caveats](#known-caveats)).

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_durable
```

You should see `pg_durable` listed with its installed SQL version.

## Known Caveats

- `pg_durable` must be loaded through `shared_preload_libraries`, and its
  background worker processes the database named by `pg_durable.database`. The
  metadata and example above configure that database as `app`; create the
  extension there.
- After startup or extension creation, `df.start` can briefly report that the
  control background worker is not yet initialized. Wait for initialization
  and retry that readiness error; configuring authentication is still required.
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
  management role (`postgres` by default) and submitting roles.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
