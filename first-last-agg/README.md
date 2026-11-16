# first-last-agg
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides first() and last() aggregates that follow an explicit ORDER BY within each aggregate. See the [upstream project](https://github.com/wulczer/first_last_agg) for its API and release history.

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
  name: cluster-first-last-agg
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
    - name: first-last-agg
```

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-first-last-agg-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-first-last-agg
  extensions:
  - ensure: present
    name: first_last_agg
```

A SQL check that exercises the installed extension is:

```sql
SELECT (SELECT first(v ORDER BY i) = 10 AND last(v ORDER BY i) = 20 FROM (VALUES (1,10),(2,20)) AS s(i,v));
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-first-last-agg` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. The first-last-agg module uses PostgreSQL licensing. Its Debian copyright file, including upstream attribution and any bundled component notices, is included under `/licenses/`.

