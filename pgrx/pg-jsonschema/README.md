# pg_jsonschema
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds support for JSON Schema validation on the `json` and `jsonb` data types.
Use it to reject JSON records that are missing required fields or contain the
wrong kinds of values.

For more information, see the [upstream documentation](https://github.com/supabase/pg_jsonschema).

### 1. Add the pg-jsonschema extension image to your Cluster

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

Define the `pg-jsonschema` extension under the `postgresql.extensions` section
of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-jsonschema
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-jsonschema
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_jsonschema;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT json_matches_schema('{"type":"integer"}'::json, '42'::json);
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
