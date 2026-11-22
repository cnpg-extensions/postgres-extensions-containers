# pg_durable
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Supports durable, fault-tolerant SQL workflows.
Use it to run a multi-step data import that can resume after a database
restart.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/microsoft/pg_durable).

### 1. Add the pg-durable extension image to your Cluster

This example runs SQL workflows for one application in the `app` database.
The application keeps its database owner separate from `workflow_runner`, a
dedicated login for submitting and executing workflows. CNPG manages that
login. HTTP activities are disabled for this SQL-only workload. Superuser
workflows are disabled by default.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-durable
spec:
  imageCatalogRef: ...
  managed:
    roles:
    - name: workflow_runner
      login: true
  postgresql:
    parameters:
      pg_durable.database: app
      pg_durable.http_security: disabled
    pg_ident:
    - local postgres workflow_runner
    shared_preload_libraries:
    - pg_durable
    extensions:
    - name: pg-durable
```

### 2. Enable the extension in a database

As an administrator in the `app` database, install the extension and grant
the runner permission to submit workflows.

```sql
CREATE EXTENSION pg_durable;
SELECT df.grant_usage('workflow_runner');
```

The example workflow needs no application table
privileges. For real jobs, grant the runner access only to the schemas and
objects its SQL uses.

### 3. Verify installation

As `workflow_runner` in the `app` database, run this two-step workflow in
`psql` and save its ID.

```sql
SET search_path TO pg_catalog, df;
SELECT df.start(
  $$SELECT 40 AS n$$ |=> 'first'
  ~> $$SELECT $first.n + 2 AS answer, current_user AS ran_as$$
) AS id \gset
```

Check the same ID in that session. Once the status is `completed`, the result
should contain one row with `answer` equal to `42` and `ran_as` equal to `workflow_runner`.

```sql
SELECT df.status(:'id');
SELECT df.result(:'id');
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
