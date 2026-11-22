# Apache AGE
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides graph database functionality, enabling you to store, query, and
analyze graph data using Cypher queries alongside SQL. Use it to find
connections in your data, such as friends of friends. It is based on the
openCypher graph query language.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://age.apache.org/).

### 1. Add the age extension image to your Cluster

This extension requires `age` in `shared_preload_libraries`, as shown below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-age
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - age
    extensions:
    - name: age
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION age;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

AGE installs its functions and types in `ag_catalog`. Use schema-qualified
names such as `ag_catalog.cypher(...)` and `ag_catalog.agtype`, or add
`ag_catalog` to your session's `search_path` to use unqualified names.

### 3. Verify installation

```sql
SELECT ag_catalog.age_size('[1, 2, 3]'::ag_catalog.agtype);
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
