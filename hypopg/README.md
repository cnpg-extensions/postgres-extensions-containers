# hypopg
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[HypoPG](https://github.com/HypoPG/hypopg) provides hypothetical indexes for
PostgreSQL. It lets you compare query plans with an index that has not been
physically created.

## Usage

Add the image to a Cluster:

~~~yaml
postgresql:
  extensions:
  - name: hypopg
    image:
      # renovate: suite=trixie-pgdg depName=postgresql-18-hypopg
      reference: ghcr.io/cnpg-extensions/hypopg:1.4.4-18-trixie
~~~

Enable the SQL extension in a Database:

~~~yaml
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
    # renovate: suite=trixie-pgdg depName=postgresql-18-hypopg extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '1.4.4'
~~~

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
