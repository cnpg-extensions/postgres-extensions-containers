# tds_fdw
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

tds_fdw is a PostgreSQL Foreign Data Wrapper (FDW) that enables PostgreSQL to
query Microsoft SQL Server and Sybase databases using the TDS (Tabular Data
Stream) protocol via FreeTDS.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

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

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION tds_fdw;` in the target database.

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
\dx tds_fdw
```

You should see `tds_fdw` listed with its installed SQL version.

## Known Caveats

- **External database required**: Foreign table queries require a running
  TDS-compatible database server and `CREATE SERVER` / `CREATE USER MAPPING`
  configuration.
- **Runtime library dependency**: The FreeTDS library (`libsybdb5`) is bundled
  in the image under `/system/`.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
