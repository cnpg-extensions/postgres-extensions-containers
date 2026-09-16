# show-plans
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_show_plans](https://github.com/cybertec-postgresql/pg_show_plans) shows the
query plans of currently running PostgreSQL statements. Plans can be returned
as plain text, JSON, YAML, or XML.

## Usage

Add the image to a Cluster and preload pg_show_plans:

~~~yaml
postgresql:
  shared_preload_libraries:
  - pg_show_plans
  extensions:
  - name: show-plans
    image:
      # renovate: suite=trixie-pgdg depName=postgresql-18-show-plans
      reference: ghcr.io/cnpg-extensions/show-plans:2.1.8-18-trixie
~~~

Enable the SQL extension in a Database:

~~~yaml
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
    # renovate: suite=trixie-pgdg depName=postgresql-18-show-plans extractVersion=^(?<version>\d+\.\d+)
    version: '2.1'
~~~

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
