# orafce
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Implements a subset of Oracle-compatible SQL functions and packages, including NVL. See the [upstream project](https://github.com/orafce/orafce) for its API and release history.

## Use with CloudNativePG

Add this image to a PostgreSQL 18 Cluster on Trixie. Choose the Bookworm image tag when the base image uses Bookworm.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-orafce
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
    - name: orafce
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-orafce
        reference: ghcr.io/cnpg-extensions/orafce:4.16.13-18-trixie
```

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-orafce-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-orafce
  extensions:
  - ensure: present
    name: orafce
    # renovate: suite=trixie-pgdg depName=postgresql-18-orafce extractVersion=^(?<version>\d+\.\d+)
    version: '4.16'
```

A SQL check that exercises the installed extension is:

```sql
SELECT oracle.nvl(NULL::integer, 7) = 7;
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-orafce` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. The orafce module uses 0BSD, GPL-3.0-or-later WITH Bison-exception-2.2 licensing. Its Debian copyright file is included under `/licenses/`. For the generated parser, Debian identifies `sqlparse.c` and `sqlparse.h` as GPL-3.0-or-later WITH Bison-exception-2.2.

