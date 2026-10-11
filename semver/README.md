# semver
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides a semantic-version data type with comparison and ordering operators. See the [upstream project](https://pgxn.org/dist/semver/doc/semver.html) for its API and release history.

## Use with CloudNativePG

Add this image to a PostgreSQL 18 Cluster on Trixie. Choose the Bookworm image tag when the base image uses Bookworm.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-semver
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
    - name: semver
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-semver
        reference: ghcr.io/cnpg-extensions/semver:0.42.0-18-trixie
```

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-semver-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-semver
  extensions:
  - ensure: present
    name: semver
    # renovate: suite=trixie-pgdg depName=postgresql-18-semver extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '0.42.0'
```

A SQL check that exercises the installed extension is:

```sql
SELECT '1.2.3'::semver < '1.3.0'::semver;
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-semver` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. The semver module uses PostgreSQL licensing. Its Debian copyright file, including upstream attribution and any bundled component notices, is included under `/licenses/`.

