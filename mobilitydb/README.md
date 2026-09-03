# MobilityDB
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[MobilityDB](https://mobilitydb.com/) is a PostgreSQL extension that adds support for temporal and spatio-temporal data types. It enables moving object databases for tracking positions, trajectories, and other time-varying spatial attributes. MobilityDB extends PostGIS with temporal types for geographic data.

## Usage

### 1. Add the mobilitydb extension image to your Cluster

Define the `mobilitydb` extension under the `postgresql.extensions` section of
your `Cluster` resource. MobilityDB **requires PostGIS** to be loaded first.
For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-mobilitydb
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: postgis
      image:
        reference: ghcr.io/cloudnative-pg/postgis:3.5.3-18-trixie
    - name: mobilitydb
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-mobilitydb
        reference: ghcr.io/cnpg-extensions/mobilitydb:1.3.0-18-trixie
```

### 2. Enable the extension in a database

You can install `mobilitydb` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. PostGIS must be installed first. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-mobilitydb-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-mobilitydb
  extensions:
  - name: postgis
    version: '3.5'
  - name: mobilitydb
    # renovate: suite=trixie-pgdg depName=postgresql-18-mobilitydb extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '1.3.0'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION mobilitydb;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `mobilitydb` listed among the installed extensions.

## Known Caveats

- **Requires PostGIS**: MobilityDB depends on PostGIS. You must include the
  PostGIS extension image in your cluster and create the `postgis` extension
  before creating `mobilitydb`. The `required_extensions` field in the metadata
  enforces this ordering.
- **Runtime library dependency**: This extension requires GEOS and other spatial
  libraries at runtime. These are bundled in the image under `/system/`.
- **License**: MobilityDB is licensed under GPL-2+ and GPL-3+, which is why it
  is hosted in the CNPG Extensions project rather than upstream.
- **Testing limitation**: The CI tests verify basic extension installation.
  Full spatio-temporal query functionality was not exercised in integration tests.

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

All relevant license and copyright information for the `mobilitydb` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
