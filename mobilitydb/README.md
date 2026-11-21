# MobilityDB
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds support for temporal and spatio-temporal data types. Use it to track
where something was at a particular time, such as a vehicle along its route.
MobilityDB extends PostGIS with temporal types for geographic data.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://mobilitydb.com/).

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
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: postgis
    - name: mobilitydb
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION mobilitydb;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

Install `postgis`, then `mobilitydb` in that order.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx mobilitydb
```

You should see `mobilitydb` listed with its installed SQL version.

## Known Caveats

- **Requires PostGIS**: MobilityDB depends on PostGIS. You must include the
  PostGIS extension image in your cluster and create the `postgis` extension
  before creating `mobilitydb`. The `required_extensions` field in the metadata
  enforces this ordering.
- **Runtime library dependency**: This extension requires GEOS and other spatial
  libraries at runtime. These are bundled in the image under `/system/`.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
