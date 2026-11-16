# extra-window-functions
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds window functions such as lag_ignore_nulls and lead_ignore_nulls. See the [upstream project](https://github.com/xocolatl/extra_window_functions) for its API and release history.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Use with CloudNativePG

Select this extension from the Trixie catalog for PostgreSQL 18. Use
`postgresql-minimal-bookworm` for an existing Bookworm cluster.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-extra-window-functions
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
    - name: extra-window-functions
```

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-extra-window-functions-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-extra-window-functions
  extensions:
  - ensure: present
    name: extra_window_functions
```

A SQL check that exercises the installed extension is:

```sql
SELECT (SELECT lag_value = 10 FROM (SELECT i, lag_ignore_nulls(v) OVER (ORDER BY i) AS lag_value FROM (VALUES (1,10),(2,NULL),(3,20)) AS s(i,v)) AS windowed WHERE i=3);
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-extra-window-functions` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. The extra-window-functions module uses PostgreSQL licensing. Its Debian copyright file, including upstream attribution and any bundled component notices, is included under `/licenses/`.

