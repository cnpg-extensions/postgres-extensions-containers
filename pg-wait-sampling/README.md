# pg-wait-sampling
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Samples PostgreSQL wait events and exposes current,
historical, and aggregated profile views in SQL.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/postgrespro/pg_wait_sampling).

### 1. Add the pg-wait-sampling extension image to your Cluster

Add the extension image and preload its worker in a complete Cluster definition:

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

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pg_wait_sampling
```

You should see `pg_wait_sampling` listed with its installed SQL version.

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
