# hypopg
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[HypoPG](https://github.com/HypoPG/hypopg) provides hypothetical indexes for
PostgreSQL. It lets you compare query plans with an index that has not been
physically created.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the hypopg extension image to your Cluster

Add the image to a Cluster:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-hypopg
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: hypopg
```

### 2. Enable the extension in a database

Enable the SQL extension in a Database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-hypopg-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-hypopg
  extensions:
  - name: hypopg
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Create a hypothetical index and inspect the resulting plan:

~~~sql
CREATE EXTENSION hypopg;
SELECT * FROM hypopg_create_index('CREATE INDEX ON my_table (column_name)');
EXPLAIN SELECT * FROM my_table WHERE column_name = 1;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-hypopg/.
