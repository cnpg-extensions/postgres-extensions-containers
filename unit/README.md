# unit
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides SI unit values, conversions and arithmetic. See the [upstream project](https://github.com/df7cb/postgresql-unit) for its API and release history.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the unit extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-unit
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: unit
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION unit;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

A SQL check that exercises the installed extension is:

```sql
SELECT '1 m'::unit = '100 cm'::unit;
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-unit` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. Its control file requires `plpgsql`, which PostgreSQL provides in the CNPG base image. The unit module uses GPL-3.0-or-later licensing. Its Debian copyright file is included under `/licenses/`.

The PGDG installation and upgrade SQL reads `unit_prefixes.data` and `unit_units.data` from Debian's `/usr/share/postgresql/18/extension` directory. CNPG mounts extension-image files under `/extensions/unit`, so the image build applies the GPL-licensed patch at `unit/patches/0001-use-cnpg-mounted-data-files.patch` in this repository to point all 14 data-file reads at `/extensions/unit/share/extension`. The data files and patched SQL scripts are shipped together in the mounted image payload; users do not need to edit the database container.
