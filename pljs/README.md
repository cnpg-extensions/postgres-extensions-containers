# PL/JS
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

PL/JS provides a trusted JavaScript procedural language for PostgreSQL, backed by QuickJS statically compiled into `pljs.so`. See the [upstream project](https://github.com/plv8/pljs) for its API and release history.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pljs extension image to your Cluster

Mount the extension image into PostgreSQL 18:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pljs
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pljs
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pljs;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

A function exercises the JavaScript runtime:

```sql
CREATE FUNCTION js_double(a integer) RETURNS integer
LANGUAGE pljs AS $$ return a * 2; $$;
SELECT js_double(21); -- 42
```

The language is trusted, but the extension itself must be installed by a database superuser. Continue to apply PostgreSQL's normal function and schema privileges to JavaScript functions. The included example performs SQL-only work.  If application functions are extended to write files through other installed interfaces, declaratively provide a volume with suitable ownership/access, retention, and cleanup before enabling that workflow.

## Package, dependency and license notes

PGDG package `postgresql-18-pljs` supplies `pljs.so` and its control/SQL files. QuickJS is statically linked, so no additional runtime package is needed. The PGDG package copyright notice is under `/licenses`.

PLJS uses a project-specific license recorded as `LicenseRef-PLJS` in the image metadata. The Debian copyright file preserves its full terms; QuickJS is MIT licensed. Renovate tracks `postgresql-18-pljs`; inspect the source patch and notices when updating it.
