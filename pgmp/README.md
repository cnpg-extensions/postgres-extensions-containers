# pgmp
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pgmp](https://github.com/dvarrazzo/pgmp) is a PostgreSQL extension that provides arbitrary precision integer and rational arithmetic using the GNU Multiple Precision Arithmetic Library (GMP). It adds `mpz` (integer) and `mpq` (rational) data types with full arithmetic support.

## Usage

### 1. Add the pgmp extension image to your Cluster

Define the `pgmp` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgmp
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pgmp
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pgmp
        reference: ghcr.io/cnpg-extensions/pgmp:1.0.6-18-trixie
```

### 2. Enable the extension in a database

You can install `pgmp` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgmp-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgmp
  extensions:
  - name: pgmp
    # renovate: suite=trixie-pgdg depName=postgresql-18-pgmp extractVersion=^(?<version>\d+\.\d+)
    version: '1.1'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pgmp;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pgmp` listed among the installed extensions.

## Known Caveats

- **Non-standard SQL directory**: The `pgmp.control` file specifies
  `directory = 'pgmp'`, so SQL migration scripts are installed in
  `/usr/share/postgresql/<version>/pgmp/` rather than the standard `extension/`
  subdirectory. The Dockerfile handles this with an additional `COPY` for the
  `pgmp/` directory.
- **License**: `pgmp` is LGPL-3+, which is why it is hosted in the
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

All relevant license and copyright information for the `pgmp` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
