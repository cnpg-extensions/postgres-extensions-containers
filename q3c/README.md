# q3c
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[q3c](https://github.com/segasai/q3c) (Quad Tree Cube) is a PostgreSQL extension for indexing and querying sky survey data using spherical coordinate systems. It provides efficient spatial indexing of astronomical objects (stars, galaxies) by right ascension and declination, enabling fast cone searches and neighbor lookups.

## Usage

### 1. Add the q3c extension image to your Cluster

Define the `q3c` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-q3c
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: q3c
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-q3c
        reference: ghcr.io/cnpg-extensions/q3c:2.0.2-18-trixie
```

### 2. Enable the extension in a database

You can install `q3c` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-q3c-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-q3c
  extensions:
  - name: q3c
    # renovate: suite=trixie-pgdg depName=postgresql-18-q3c extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '2.0.2'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION q3c;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `q3c` listed among the installed extensions.

## Known Caveats

- **License**: `q3c` is GPL-2+, which is why it is hosted in the
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

All relevant license and copyright information for the `q3c` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
