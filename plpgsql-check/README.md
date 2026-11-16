# plpgsql-check
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[plpgsql_check](https://github.com/okbob/plpgsql_check) is a linter for
PL/pgSQL. It checks embedded SQL and PL/pgSQL behavior that PostgreSQL's
function validator cannot detect at function creation time.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the plpgsql-check extension image to your Cluster

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

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Check a PL/pgSQL function with:

~~~sql
CREATE EXTENSION plpgsql_check;
SELECT * FROM plpgsql_check_function('my_function()');
~~~

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-plpgsql-check/.
