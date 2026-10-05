# pgsentinel
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pgsentinel](https://github.com/pgsentinel/pgsentinel) samples active session
history into an in-memory ring buffer and links session activity with
pg_stat_statements.

## Usage

Add the image to a Cluster and preload both libraries:

~~~yaml
postgresql:
  shared_preload_libraries:
  - pg_stat_statements
  - pgsentinel
  extensions:
  - name: pgsentinel
    image:
      # renovate: suite=trixie-pgdg depName=postgresql-18-pgsentinel
      reference: ghcr.io/cnpg-extensions/pgsentinel:1.5.1-18-trixie
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
    # renovate: suite=trixie-pgdg depName=postgresql-18-pgsentinel extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '1.5.1'
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
