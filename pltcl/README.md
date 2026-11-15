# PL/Tcl
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

PL/Tcl runs Tcl functions inside PostgreSQL. This image supplies the trusted `pltcl` and untrusted `pltclu` variants with Tcl 8.6's shared library and standard script library. See the [PostgreSQL 18 PL/Tcl documentation](https://www.postgresql.org/docs/18/pltcl.html).

## Use with CloudNativePG

Mount the image into PostgreSQL 18:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pltcl
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
    - name: pltcl
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-pltcl-18
        reference: ghcr.io/cnpg-extensions/pltcl:18.7-18-trixie
      ld_library_path:
      - system
      env:
      - name: TCL_LIBRARY
        value: ${image_root}/share/tcl8.6
      - name: TCL8_6_TM_PATH
        value: ${image_root}/share/tcl8.6/tcl8
```

Enable trusted PL/Tcl in a database with a `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pltcl-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pltcl
  extensions:
  - ensure: present
    name: pltcl
    # SQL version must be checked in the package control files before merging updates.
    version: "1.0"
```

A trusted Tcl function can perform simple computation:

```sql
CREATE FUNCTION tcl_add(a integer, b integer) RETURNS integer
AS $$ return [expr {$1 + $2}] $$ LANGUAGE pltcl;
SELECT tcl_add(19, 23); -- 42
```

`pltcl` uses Tcl's safe interpreter, which omits commands such as `exec` and `open`; it cannot access the host filesystem or launch processes directly. To install the untrusted variant, a superuser runs `CREATE EXTENSION pltclu;`. Only superusers can create `pltclu` functions. Those functions run as the PostgreSQL operating-system user with its available filesystem, process and network access. Review untrusted function code and privileges carefully. The included examples perform SQL-only work.  Before enabling `pltclu` functions that produce persistent files, declaratively provide a volume with suitable ownership/access, retention, and cleanup; the image does not define an application data-storage lifecycle.

The extension configuration adds the image's `/system` directory to the loader path, sets `TCL_LIBRARY` to the packaged Tcl 8.6 scripts, and sets `TCL8_6_TM_PATH` to its modules, including `msgcat` used by date functions. Users need no package installation or filesystem changes in the database container.

## Package, dependency and license notes

PGDG `postgresql-pltcl-18` provides both language control/SQL sets and `pltcl.so`. Debian `libtcl8.6` is the dynamically linked interpreter, with its script library copied to the extension image and native dependencies under `/system`. Package copyright notices are under `/licenses`.

Renovate tracks `postgresql-pltcl-18`; Debian Tcl updates are reviewed separately. Rebuild when either changes.

## Contributors

Maintained by [@ardentperf](https://github.com/ardentperf).
