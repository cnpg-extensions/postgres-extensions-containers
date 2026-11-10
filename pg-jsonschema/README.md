# pg_jsonschema
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_jsonschema](https://github.com/supabase/pg_jsonschema) is a PostgreSQL
extension that adds support for [JSON Schema](https://json-schema.org/)
validation on the `json` and `jsonb` data types. JSON Schema describes the
expected structure and constraints of JSON documents, allowing the extension
to validate values, check schemas, and report validation errors directly in
SQL.

## Usage

### 1. Add the pg-jsonschema extension image to your Cluster

Define the `pg-jsonschema` extension under the `postgresql.extensions` section
of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-jsonschema
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg-jsonschema
      image:
        reference: ghcr.io/cnpg-extensions/pg-jsonschema:v0.3.4-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_jsonschema` in a specific database by creating or updating
a `Database` resource, or by running `CREATE EXTENSION` directly in `psql`.
For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-jsonschema-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-jsonschema
  extensions:
  - name: pg_jsonschema
    version: '0.3.4'
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_jsonschema;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_jsonschema` listed among the installed extensions.

## Contributors

Maintained by Jeremy Schneider (@ardentperf).

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
