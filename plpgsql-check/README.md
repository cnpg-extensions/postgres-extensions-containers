# plpgsql-check
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[plpgsql_check](https://github.com/okbob/plpgsql_check) is a linter for
PL/pgSQL. It checks embedded SQL and PL/pgSQL behavior that PostgreSQL's
function validator cannot detect at function creation time.

## Usage

Add the image to a Cluster:

~~~yaml
postgresql:
  extensions:
  - name: plpgsql-check
    image:
      # renovate: suite=trixie-pgdg depName=postgresql-18-plpgsql-check
      reference: ghcr.io/cnpg-extensions/plpgsql-check:2.10.10-18-trixie
~~~

Enable the SQL extension in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-plpgsql-check-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-plpgsql-check
  extensions:
  - name: plpgsql_check
    # The SQL extension version is 2.10; the package version is 2.10.9.
    # renovate: suite=trixie-pgdg depName=postgresql-18-plpgsql-check extractVersion=^(?<version>\d+\.\d+)
    version: '2.10'
~~~

Check a PL/pgSQL function with:

~~~sql
CREATE EXTENSION plpgsql_check;
SELECT * FROM plpgsql_check_function('my_function()');
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-plpgsql-check/.
