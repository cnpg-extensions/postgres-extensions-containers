# PL/Tcl
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[PL/Tcl](https://www.postgresql.org/docs/18/pltcl.html) lets you write PostgreSQL functions in Tcl. It provides the trusted
`pltcl` and untrusted `pltclu` language variants.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://www.postgresql.org/docs/18/pltcl.html).

### 1. Add the pltcl extension image to your Cluster

Mount the image into your Cluster:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pltcl
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pltcl
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pltcl;` in the target database.

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
\dx pltcl
```

You should see `pltcl` listed with its installed SQL version.

A trusted Tcl function can perform simple computation:

```sql
CREATE FUNCTION tcl_add(a integer, b integer) RETURNS integer
AS $$ return [expr {$1 + $2}] $$ LANGUAGE pltcl;
SELECT tcl_add(19, 23); -- 42
```

`pltcl` uses Tcl's safe interpreter, which omits commands such as `exec` and `open`; it cannot access the host filesystem or launch processes directly. To install the untrusted variant, a superuser runs `CREATE EXTENSION pltclu;`. Only superusers can create `pltclu` functions. Those functions run as the PostgreSQL operating-system user with its available filesystem, process and network access. Review untrusted function code and privileges carefully. The included examples perform SQL-only work.  Before enabling `pltclu` functions that produce persistent files, declaratively provide a volume with suitable ownership/access, retention, and cleanup; the image does not define an application data-storage lifecycle.

The extension configuration adds the image's `/system` directory to the loader path, sets `TCL_LIBRARY` to the packaged Tcl 8.6 scripts, and sets `TCL8_6_TM_PATH` to its modules, including `msgcat` used by date functions. Users need no package installation or filesystem changes in the database container.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
