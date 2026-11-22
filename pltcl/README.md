# PL/Tcl
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Lets you write PostgreSQL functions in Tcl. For example, update a row’s change
counter automatically with a small Tcl script.

This image includes both `pltcl` and `pltclu`, which you can enable separately.
Use `pltcl`, the trusted Tcl language, for normal use. The untrusted `pltclu`
language can access files, run programs, and use the network as PostgreSQL’s
operating-system user; reserve it for exceptional cases requiring that level
of access.

For more information, see the [upstream documentation](https://www.postgresql.org/docs/18/pltcl.html).

### 1. Add the pltcl extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

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

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

A trusted Tcl function can perform simple computation:

```sql
CREATE FUNCTION tcl_add(a integer, b integer) RETURNS integer
AS $$ return [expr {$1 + $2}] $$ LANGUAGE pltcl;
SELECT tcl_add(19, 23); -- 42
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
