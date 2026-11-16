# tdigest
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides t-digest aggregates for approximate quantile and percentile calculations. See the [upstream project](https://github.com/tvondra/tdigest) for its API and release history.

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
  name: cluster-tdigest
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
    - name: tdigest
```

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-tdigest-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-tdigest
  extensions:
  - ensure: present
    name: tdigest
```

A SQL check that exercises the installed extension is:

```sql
SELECT (SELECT tdigest_percentile(i::float8, 100, 0.5::float8) BETWEEN 45 AND 55 FROM generate_series(1,100) AS s(i));
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-tdigest` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. The tdigest module uses PostgreSQL licensing. Its Debian copyright file, including upstream attribution and any bundled component notices, is included under `/licenses/`.

