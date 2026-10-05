# pg-stat-kcache
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_stat_kcache](https://github.com/powa-team/pg_stat_kcache) collects
per-query kernel statistics, including CPU time and filesystem reads and
writes. It uses the query identifiers supplied by the bundled
pg_stat_statements extension.

## Usage

Add the image to a Cluster and preload both libraries:

~~~yaml
postgresql:
  shared_preload_libraries:
  - pg_stat_statements
  - pg_stat_kcache
  extensions:
  - name: pg-stat-kcache
    image:
      # renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-kcache
      reference: ghcr.io/cnpg-extensions/pg-stat-kcache:2.3.2-18-trixie
~~~

Enable the SQL extension in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-stat-kcache-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-stat-kcache
  extensions:
  - name: pg_stat_statements
  - name: pg_stat_kcache
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-kcache extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '2.3.2'
~~~

After running queries, inspect the collected values:

~~~sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_stat_kcache;
SELECT * FROM pg_stat_kcache;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-pg-stat-kcache/.
