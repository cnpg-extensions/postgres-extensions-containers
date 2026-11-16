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
inherit image references and runtime settings from the catalog.

## Usage

Add the image to a Cluster and preload both libraries:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgsentinel
spec:
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    shared_preload_libraries:
    - pg_stat_statements
    - pgsentinel
    extensions:
    - name: pgsentinel
~~~

Enable the SQL extension in a Database:

~~~yaml
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
~~~

After the cluster has run for a few seconds, inspect the active session
history:

~~~sql
CREATE EXTENSION IF NOT EXISTS pgsentinel;
SELECT * FROM pg_active_session_history LIMIT 5;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-pgsentinel/.
