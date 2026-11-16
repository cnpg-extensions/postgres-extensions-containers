# orafce
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Implements a subset of Oracle-compatible SQL functions and packages, including NVL. See the [upstream project](https://github.com/orafce/orafce) for its API and release history.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the orafce extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-orafce
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: orafce
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION orafce;` in the target database.

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
SELECT oracle.nvl(NULL::integer, 7) = 7;
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-orafce` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. The orafce module uses 0BSD, GPL-3.0-or-later WITH Bison-exception-2.2 licensing. Its Debian copyright file is included under `/licenses/`. For the generated parser, Debian identifies `sqlparse.c` and `sqlparse.h` as GPL-3.0-or-later WITH Bison-exception-2.2.

