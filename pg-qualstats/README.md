# pg-qualstats
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_qualstats](https://github.com/powa-team/pg_qualstats) gathers statistics
about predicates found in WHERE and JOIN clauses. The statistics help
identify frequently used predicates and potentially missing indexes.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-qualstats extension image to your Cluster

Add the image to a Cluster and preload pg_qualstats:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-qualstats
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_qualstats
    extensions:
    - name: pg-qualstats
```

### 2. Enable the extension in a database

Enable the SQL extension in a Database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-qualstats-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-qualstats
  extensions:
  - name: pg_qualstats
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Inspect the gathered predicate statistics with:

~~~sql
CREATE EXTENSION pg_qualstats;
SELECT * FROM pg_qualstats;
~~~

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-pg-qualstats/.
