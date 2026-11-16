# toastinfo
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[toastinfo](https://github.com/df7cb/toastinfo) describes how PostgreSQL
stores variable-length values, including inline, compressed, and out-of-line
TOAST values. It does not need to be preloaded.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the image to a Cluster:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-toastinfo
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
    - name: toastinfo
~~~

Enable the SQL extension in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-toastinfo-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-toastinfo
  extensions:
  - name: toastinfo
~~~

Use pg_toastinfo and pg_toastpointer to inspect a value:

~~~sql
CREATE EXTENSION toastinfo;
SELECT pg_toastinfo(value), pg_toastpointer(value) FROM my_table;
~~~

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-toastinfo/.
