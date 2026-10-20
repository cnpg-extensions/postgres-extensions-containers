# pg_session_jwt
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_session_jwt](https://github.com/neondatabase/pg_session_jwt) is a
PostgreSQL extension for managing authenticated sessions through JSON Web
Tokens (JWTs). With a JSON Web Key (JWK), it verifies JWT authenticity and
exposes the validated claims to SQL. Without a JWK, it can use PostgREST-
compatible JWT claims for identifying the current user.

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
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg-session-jwt
      image:
        reference: ghcr.io/cnpg-extensions/pg-session-jwt:v0.5.0-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_session_jwt` in a specific database by creating or
updating a `Database` resource, or by running `CREATE EXTENSION` directly in
`psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-session-jwt-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-session-jwt
  extensions:
  - name: pg-session-jwt
    version: '0.5.0'
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_session_jwt;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_session_jwt` listed among the installed extensions.

## Known Caveats

- When using JWK validation, set `pg_session_jwt.jwk` before creating the
  connection. It can be configured at postmaster startup, in the PostgreSQL
  configuration file, or through the `PGOPTIONS` connection environment.
- Without JWK validation, `request.jwt.claims` is a regular PostgreSQL
  parameter that database users may be able to modify. Use this mode only when
  the claims are set by a trusted integration such as PostgREST.

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

All relevant license and copyright information for the `pg_session_jwt`
extension and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
