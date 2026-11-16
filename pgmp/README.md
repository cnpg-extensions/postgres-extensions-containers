# pgmp
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pgmp](https://github.com/dvarrazzo/pgmp) is a PostgreSQL extension that provides arbitrary precision integer and rational arithmetic using the GNU Multiple Precision Arithmetic Library (GMP). It adds `mpz` (integer) and `mpq` (rational) data types with full arithmetic support.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

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
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pgmp
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pgmp;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

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
