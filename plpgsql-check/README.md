# plpgsql-check
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[plpgsql_check](https://github.com/okbob/plpgsql_check) is a linter for
PL/pgSQL. It checks embedded SQL and PL/pgSQL behavior that PostgreSQL's
function validator cannot detect at function creation time.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the image to a Cluster:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-plpgsql-check
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
    extensions:
    - name: plpgsql-check
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
