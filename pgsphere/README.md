# pgSphere
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pgSphere](https://pgsphere.github.io/) is a PostgreSQL extension that provides spherical geometry data types and operators for astronomical and geographical data. It supports types such as spherical points, circles, ellipses, lines, polygons, and boxes, along with indexing via GiST.

## Usage

### 1. Add the pgsphere extension image to your Cluster

Define the `pgsphere` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgsphere
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pgsphere
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pgsphere
        reference: ghcr.io/cnpg-extensions/pgsphere:1.5.2-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_sphere` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgsphere-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgsphere
  extensions:
  - name: pgsphere
    # renovate: suite=trixie-pgdg depName=postgresql-18-pgsphere extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '1.5.2'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_sphere;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_sphere` listed among the installed extensions.

## Known Caveats

- **Runtime library dependency**: This extension requires HEALPIX and other
  astronomical libraries at runtime. These are bundled in the image under
  `/system/`.
- **License**: `pgsphere` is GPL-3+, which is why it is hosted in the
  CNPG Extensions project rather than upstream.

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pgsphere` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
