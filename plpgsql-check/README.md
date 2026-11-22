# plpgsql-check
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Lints PL/pgSQL. Use it to catch mistakes such as a misspelled column name
before a function runs.

For more information, see the [upstream documentation](https://github.com/okbob/plpgsql_check).

### 1. Add the plpgsql-check extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

Add the image to a Cluster:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-plpgsql-check
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: plpgsql-check
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION plpgsql_check;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Check a PL/pgSQL function with:

~~~sql
CREATE FUNCTION checked_example() RETURNS integer LANGUAGE plpgsql AS $$
BEGIN
  RETURN 1;
END;
$$;
SELECT * FROM plpgsql_check_function('checked_example()');
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
