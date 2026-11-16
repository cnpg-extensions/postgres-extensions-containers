# show-plans
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_show_plans](https://github.com/cybertec-postgresql/pg_show_plans) shows the
query plans of currently running PostgreSQL statements. Plans can be returned
as plain text, JSON, YAML, or XML.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the show-plans extension image to your Cluster

Add the image to a Cluster and preload pg_show_plans:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-show-plans
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_show_plans
    extensions:
    - name: show-plans
```

### 2. Enable the extension in a database

Enable the SQL extension in a Database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-show-plans-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-show-plans
  extensions:
  - name: pg_show_plans
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Inspect plans for currently running statements:

~~~sql
CREATE EXTENSION pg_show_plans;
SELECT * FROM pg_show_plans;
SELECT * FROM pg_show_plans_q;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-show-plans/.
