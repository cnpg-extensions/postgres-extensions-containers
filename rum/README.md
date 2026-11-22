# rum
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds the RUM index access method, including full-text search indexing and
ordering support. Use it to search documents for a phrase and show the best
matches first.

For more information, see the [upstream documentation](https://github.com/postgrespro/rum).

### 1. Add the rum extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-rum
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: rum
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION rum;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

A SQL check that exercises the installed extension is:

```sql
SELECT to_tsvector('english', 'postgres database') @@ to_tsquery('english', 'postgres');
```

For RUM, create the index using its access method to exercise the additional index behavior:

```sql
CREATE TEMP TABLE rum_demo (id integer, doc tsvector);
INSERT INTO rum_demo VALUES
  (1, to_tsvector('english', 'postgres database')),
  (2, to_tsvector('english', 'other document'));
CREATE INDEX ON rum_demo USING rum (doc rum_tsvector_ops);
SELECT id FROM rum_demo WHERE doc @@ to_tsquery('english', 'postgres');
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
