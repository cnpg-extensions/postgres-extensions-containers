# rum
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds the RUM index access method, including full-text search indexing and ordering support. See the [upstream project](https://github.com/postgrespro/rum) for its API and release history.

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
  name: cluster-rum
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
    - name: rum
```

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-rum-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-rum
  extensions:
  - ensure: present
    name: rum
```

A SQL check that exercises the installed extension is:

```sql
SELECT to_tsvector('english', 'postgres database') @@ to_tsquery('english', 'postgres');
```

For RUM, create the index using its access method to exercise the additional index behavior:

```sql
CREATE TEMP TABLE rum_demo (id integer, doc tsvector);
INSERT INTO rum_demo VALUES
  (1, to_tsvector('english', 'postgres database')),
  (2, to_tsvector('english', 'other document'));
CREATE INDEX ON rum_demo USING rum (doc rum_tsvector_ops);
SELECT id FROM rum_demo WHERE doc @@ to_tsquery('english', 'postgres');
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-rum` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. RUM links to `libm.so.6`, supplied by the CNPG base image. The rum module uses PostgreSQL licensing. Its Debian copyright file, including upstream attribution and any bundled component notices, is included under `/licenses/`.

