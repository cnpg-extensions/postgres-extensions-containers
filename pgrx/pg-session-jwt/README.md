# pg_session_jwt
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pg_session_jwt is a PostgreSQL extension for managing authenticated sessions
through JSON Web Tokens (JWTs). With a JSON Web Key (JWK), it verifies JWT
authenticity and exposes the validated claims to SQL. Without a JWK, it can use
PostgREST-compatible JWT claims for identifying the current user.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the pg-session-jwt extension image to your Cluster

Define the `pg-session-jwt` extension under the `postgresql.extensions` section
of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-session-jwt
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-session-jwt
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_session_jwt;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_session_jwt
```

You should see `pg_session_jwt` listed with its installed SQL version.

## Known Caveats

- When using JWK validation, set `pg_session_jwt.jwk` before creating the
  connection. It can be configured at postmaster startup, in the PostgreSQL
  configuration file, or through the `PGOPTIONS` connection environment.
- Without JWK validation, `request.jwt.claims` is a regular PostgreSQL
  parameter that database users may be able to modify. Use this mode only when
  the claims are set by a trusted integration such as PostgREST.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
