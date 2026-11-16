# prefix
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides prefix ranges over text values for prefix-based lookup and indexing. See the [upstream project](https://github.com/dimitri/prefix) for its API and release history.

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
  name: cluster-prefix
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
    - name: prefix
```

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-prefix-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-prefix
  extensions:
  - ensure: present
    name: prefix
```

A SQL check that exercises the installed extension is:

```sql
SELECT prefix_range('foo') @> prefix_range('foobar');
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-prefix` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. The prefix module uses BSD-2-Clause licensing. Its Debian copyright file, including upstream attribution and any bundled component notices, is included under `/licenses/`.

The SQL catalog version is maintained separately from the Debian package version; verify `default_version` in the packaged control file when updating the package.
