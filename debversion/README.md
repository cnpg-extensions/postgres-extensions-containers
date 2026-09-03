# debversion
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[debversion](https://salsa.debian.org/postgresql/postgresql-debversion) is a PostgreSQL extension that adds a native `debversion` data type for representing and sorting Debian package version strings according to the Debian versioning algorithm (as defined in Debian Policy).

## Usage

### 1. Add the debversion extension image to your Cluster

Define the `debversion` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-debversion
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: debversion
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-debversion
        reference: ghcr.io/cnpg-extensions/debversion:1.2.0-18-trixie
```

### 2. Enable the extension in a database

You can install `debversion` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-debversion-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-debversion
  extensions:
  - name: debversion
    # renovate: suite=trixie-pgdg depName=postgresql-18-debversion extractVersion=^(?<version>\d+\.\d+)
    version: '1.2'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION debversion;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `debversion` listed among the installed extensions.

## Known Caveats

- **License**: `debversion` is licensed under GPL-3+, which is why it is hosted
  in the CNPG Extensions project rather than upstream.

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

All relevant license and copyright information for the `debversion` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
