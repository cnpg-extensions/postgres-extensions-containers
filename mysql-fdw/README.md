# mysql_fdw
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[mysql_fdw](https://github.com/EnterpriseDB/mysql_fdw) is a PostgreSQL Foreign Data Wrapper (FDW) that enables PostgreSQL to query MySQL and MariaDB databases. It allows you to define foreign tables in PostgreSQL that map to MySQL/MariaDB tables and query them using standard SQL.

## Usage

### 1. Add the mysql-fdw extension image to your Cluster

Define the `mysql-fdw` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-mysql-fdw
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: mysql-fdw
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-mysql-fdw
        reference: ghcr.io/cnpg-extensions/mysql-fdw:2.9.3-18-trixie
```

### 2. Enable the extension in a database

You can install `mysql_fdw` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-mysql-fdw-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-mysql-fdw
  extensions:
  - name: mysql-fdw
    # renovate: suite=trixie-pgdg depName=postgresql-18-mysql-fdw extractVersion=^(?<version>\d+\.\d+)
    version: '2.9'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION mysql_fdw;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `mysql_fdw` listed among the installed extensions.

## Known Caveats

- **MySQL/MariaDB client library**: The extension uses `dlopen()` at runtime to
  load `libmysqlclient.so`. This library is not detected by `ldd`, so it is
  explicitly bundled in the image as `libmariadb.so.3` with a `libmysqlclient.so`
  compatibility symlink. Only MariaDB-compatible clients are tested.
- **No live database tested**: The CI tests verify that the extension can be
  created (`CREATE EXTENSION mysql_fdw`), but do not test actual connectivity
  to a MySQL or MariaDB server. Actual foreign table queries require a running
  MySQL/MariaDB instance and proper `CREATE SERVER` / `CREATE USER MAPPING`
  configuration.
- **License**: The `mysql_fdw` extension is BSD-3-Clause, but its runtime
  dependency `libmariadb3` is LGPL-2.1, which is why this extension is hosted
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

All relevant license and copyright information for the `mysql-fdw` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
