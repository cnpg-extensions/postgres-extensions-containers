# unit
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides SI unit values, conversions and arithmetic. See the [upstream project](https://github.com/df7cb/postgresql-unit) for its API and release history.

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
  name: cluster-unit
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
    - name: unit
```

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-unit-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-unit
  extensions:
  - ensure: present
    name: unit
```

A SQL check that exercises the installed extension is:

```sql
SELECT '1 m'::unit = '100 cm'::unit;
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-unit` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. Its control file requires `plpgsql`, which PostgreSQL provides in the CNPG base image. The unit module uses GPL-3.0-or-later licensing. Its Debian copyright file is included under `/licenses/`.

The PGDG installation and upgrade SQL reads `unit_prefixes.data` and `unit_units.data` from Debian's `/usr/share/postgresql/18/extension` directory. CNPG mounts extension-image files under `/extensions/unit`, so the image build applies the GPL-licensed patch at `unit/patches/0001-use-cnpg-mounted-data-files.patch` in this repository to point all 14 data-file reads at `/extensions/unit/share/extension`. The data files and patched SQL scripts are shipped together in the mounted image payload; users do not need to edit the database container.
