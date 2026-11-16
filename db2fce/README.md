# db2fce
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

DB2-compatible SQL functions and types, including date/time helpers in the db2 schema. See the [upstream project](https://github.com/credativ/db2fce) for its API and release history.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Use with CloudNativePG

Select this extension from the Trixie catalog for PostgreSQL 18. Use
`postgresql-minimal-bookworm` for an existing Bookworm cluster.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-db2fce
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
    - name: db2fce
```

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-db2fce-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-db2fce
  extensions:
  - ensure: present
    name: db2fce
```

A SQL check that exercises the installed extension is:

```sql
SELECT db2.year(date '2026-09-29') = 2026;
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-db2fce` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. This is a SQL-only package: it contains control/SQL files and no shared object. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. The db2fce module uses PostgreSQL licensing. Its Debian copyright file, including upstream attribution and any bundled component notices, is included under `/licenses/`.

