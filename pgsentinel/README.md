# pgsentinel
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Samples active session history into an in-memory ring buffer and links session
activity with pg_stat_statements.
Use it to look back at which queries were running or waiting during a recent
slowdown.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

## Dependencies and conflicts

Requires `pg_stat_statements` in the same database.

For more information, see the [upstream documentation](https://github.com/pgsentinel/pgsentinel).

### 1. Add the pgsentinel extension image to your Cluster

This extension requires `pg_stat_statements` and `pgsentinel` in
`shared_preload_libraries`, as shown below. Set `pgsentinel.db_name` to the
database where you install the extension (`app` below).

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgsentinel
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      pgsentinel.db_name: app
    shared_preload_libraries:
    - pg_stat_statements
    - pgsentinel
    extensions:
    - name: pgsentinel
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION pgsentinel;
```

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

The worker connects to `pgsentinel.db_name` (default `postgres`). Install
`pgsentinel` in that database; this example selects CNPG's application database
`app`. If the worker's database does not contain the extension, its history
remains empty even when queries run elsewhere in the cluster.

### 3. Verify installation

After the cluster has run for a few seconds, inspect the active session
history:

~~~sql
SELECT * FROM pg_active_session_history LIMIT 5;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
