# pg-stat-kcache
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Collects per-query kernel statistics, including CPU time and filesystem reads
and writes.
Use it to find which queries use the most processor time or read the most data
from disk.

For more information, see the [upstream documentation](https://github.com/powa-team/pg_stat_kcache).

## Dependencies and conflicts

Requires `pg_stat_statements` in the same database.

### 1. Add the pg-stat-kcache extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pg_stat_statements` and `pg_stat_kcache` in
`shared_preload_libraries`, as shown below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-kcache
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_stat_statements
    - pg_stat_kcache
    extensions:
    - name: pg-stat-kcache
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION pg_stat_kcache;
```

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

After running queries, inspect the collected values:

~~~sql
SELECT * FROM pg_stat_kcache;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
