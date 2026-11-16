# PL/Lua
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

PL/Lua embeds Lua 5.3 in PostgreSQL. The package provides trusted `pllua`, untrusted `plluau`, and optional hstore transform extensions. See the [PL/Lua reference](https://pllua.github.io/pllua/).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pllua extension image to your Cluster

Mount the image into PostgreSQL 18:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pllua
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pllua
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pllua;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Use a trusted Lua function:

```sql
CREATE FUNCTION lua_add(a integer, b integer) RETURNS integer
LANGUAGE pllua AS $$ return a + b $$;
SELECT lua_add(19, 23); -- 42
```

`pllua` runs inside a sandbox that exposes safe Lua operations; for example, `os.execute` is absent there. To install the untrusted language, a superuser runs `CREATE EXTENSION plluau;`. Only superusers can create `plluau` functions. The untrusted interpreter exposes Lua's operating-system functions, which run with PostgreSQL's operating-system account and its filesystem/network permissions. Do not grant `EXECUTE` on such functions without reviewing their code and effects. Optional `hstore_pllua` and `hstore_plluau` transforms require the `hstore` extension supplied by the matching CNPG PostgreSQL base image. The included example performs SQL-only work.  Before enabling `plluau` functions that produce persistent files, declaratively provide a volume with suitable ownership/access, retention, and cleanup; the image does not define an application data-storage lifecycle.

## Package and dependency notes

The image contains the PGDG extension modules/control/SQL files and Debian `liblua5.3-0` under `/system`. Package copyright notices are under `/licenses`.

Renovate tracks `postgresql-18-pllua`. Review the separately versioned Lua package and rerun trusted/untrusted tests when rebuilding after either package changes.
