# pldebugger
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pldebugger is a PostgreSQL extension that provides a server-side debugger for
PL/pgSQL functions and procedures. It enables step-by-step debugging,
breakpoints, and variable inspection for stored procedures, and is supported by
tools such as pgAdmin.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/EnterpriseDB/pldebugger).

### 1. Add the pldebugger extension image to your Cluster

Define the `pldebugger` extension under the `postgresql.extensions` section of
your `Cluster` resource. Note that `plugin_debugger` must be added to
`shared_preload_libraries`. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pldebugger
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - plugin_debugger
    extensions:
    - name: pldebugger
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pldbgapi;` in the target database.

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
\dx pldbgapi
```

You should see `pldbgapi` listed with its installed SQL version.

## Known Caveats

- **`shared_preload_libraries` required**: The `plugin_debugger` shared library
  must be listed in `shared_preload_libraries`. Without it, `CREATE EXTENSION
  pldbgapi` will fail.
- **SQL extension name differs from image name**: The extension image is named
  `pldebugger` but the PostgreSQL extension object is `pldbgapi`. Use
  `CREATE EXTENSION pldbgapi` (not `pldebugger`).

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
