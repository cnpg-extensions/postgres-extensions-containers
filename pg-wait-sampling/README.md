# pg-wait-sampling
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Samples PostgreSQL wait events and exposes current, historical, and aggregated
profile views in SQL.
Use it to find out whether slow queries are waiting for disk access or for
other queries to finish.

For more information, see the [upstream documentation](https://github.com/postgrespro/pg_wait_sampling).

### 1. Add the pg-wait-sampling extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

This extension requires `pg_wait_sampling` in `shared_preload_libraries`, as
shown below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-wait-sampling
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_wait_sampling
    extensions:
    - name: pg-wait-sampling
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_wait_sampling;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

After the library is preloaded and the extension is installed, inspect sampled waits:

~~~sql
SELECT event_type, event, sum(count) AS samples
FROM pg_wait_sampling_profile
GROUP BY event_type, event
ORDER BY samples DESC;
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
