# pgsentinel
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pgsentinel](https://github.com/pgsentinel/pgsentinel) samples active session
history into an in-memory ring buffer and links session activity with
pg_stat_statements.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pgsentinel extension image to your Cluster

Add the image to a Cluster and preload both libraries:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgsentinel
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_stat_statements
    - pgsentinel
    extensions:
    - name: pgsentinel
```

### 2. Enable the extension in a database

Enable the SQL extension in a Database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgsentinel-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgsentinel
  extensions:
  - name: pgsentinel
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

After the cluster has run for a few seconds, inspect the active session
history:

~~~sql
CREATE EXTENSION IF NOT EXISTS pgsentinel;
SELECT * FROM pg_active_session_history LIMIT 5;
~~~

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-pgsentinel/.
