# pg-partman
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_partman](https://github.com/pgpartman/pg_partman) creates and maintains
time-based and ID-based PostgreSQL partition sets. Its optional background
worker can run partition maintenance automatically.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-partman extension image to your Cluster

Add the image to a Cluster and preload the background worker:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-partman
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_partman_bgw
    extensions:
    - name: pg-partman
```

### 2. Enable the extension in a database

Enable the SQL extension in a Database, conventionally in the partman schema:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-partman-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-partman
  extensions:
  - name: pg_partman
    schema: partman
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

See the [pg_partman documentation](https://github.com/pgpartman/pg_partman/tree/development/doc)
for partition-set configuration examples.

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-partman/.
