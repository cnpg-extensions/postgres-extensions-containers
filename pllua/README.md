# PL/Lua
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

PL/Lua lets you write PostgreSQL functions in Lua. It provides trusted `pllua`,
untrusted `plluau`, and optional hstore transforms.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the pllua extension image to your Cluster

Mount the image into your Cluster:

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

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pllua
```

You should see `pllua` listed with its installed SQL version.

Use a trusted Lua function:

```sql
CREATE FUNCTION lua_add(a integer, b integer) RETURNS integer
LANGUAGE pllua AS $$ return a + b $$;
SELECT lua_add(19, 23); -- 42
```

`pllua` runs inside a sandbox that exposes safe Lua operations; for example, `os.execute` is absent there. To install the untrusted language, a superuser runs `CREATE EXTENSION plluau;`. Only superusers can create `plluau` functions. The untrusted interpreter exposes Lua's operating-system functions, which run with PostgreSQL's operating-system account and its filesystem/network permissions. Do not grant `EXECUTE` on such functions without reviewing their code and effects. Optional `hstore_pllua` and `hstore_plluau` transforms require the `hstore` extension supplied by the matching CNPG PostgreSQL base image. The included example performs SQL-only work.  Before enabling `plluau` functions that produce persistent files, declaratively provide a volume with suitable ownership/access, retention, and cleanup; the image does not define an application data-storage lifecycle.
