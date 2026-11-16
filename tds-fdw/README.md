# tds_fdw
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[tds_fdw](https://github.com/tds-fdw/tds_fdw) is a PostgreSQL Foreign Data Wrapper (FDW) that enables PostgreSQL to query Microsoft SQL Server and Sybase databases using the TDS (Tabular Data Stream) protocol via FreeTDS.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the tds-fdw extension image to your Cluster

Define the `tds-fdw` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-tds-fdw
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: tds-fdw
```

### 2. Enable the extension in a database

You can install `tds_fdw` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-tds-fdw-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-tds-fdw
  extensions:
  - name: tds_fdw
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION tds_fdw;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `tds_fdw` listed among the installed extensions.

## Known Caveats

- **No live database tested**: The CI tests verify that the extension can be
  created (`CREATE EXTENSION tds_fdw`), but do not test actual connectivity to
  a SQL Server or Sybase instance. Actual foreign table queries require a
  running TDS-compatible database server and proper `CREATE SERVER` /
  `CREATE USER MAPPING` configuration.
- **Runtime library dependency**: The FreeTDS library (`libsybdb5`) is bundled
  in the image under `/system/`.
- **License**: `tds_fdw` itself is PostgreSQL-licensed, but its runtime
  dependency `libsybdb5` (FreeTDS) is LGPL-2+, which is why this extension is
  hosted in the CNPG Extensions project rather than upstream.

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `tds-fdw` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
