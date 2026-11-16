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

Enable the SQL extension in a Database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-plpgsql-check-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-plpgsql-check
  extensions:
  - name: plpgsql_check
```

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
