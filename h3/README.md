# h3
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

h3-pg is a PostgreSQL extension that binds the Uber H3 hierarchical hexagonal
geospatial indexing system to PostgreSQL. It enables efficient geospatial
analysis using H3 cell indexes.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the h3 extension image to your Cluster

Define the `h3` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-h3
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: h3
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION h3;` in the target database.

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
\dx h3
```

You should see `h3` listed with its installed SQL version.

## Known Caveats

- **Runtime library dependency**: This extension requires `libh3-1` at runtime.
  The library is bundled in the image under `/system/`. The `ld_library_path`
  is configured to include this directory automatically.
- **License**: The H3 library (`libh3`) itself is Apache-2.0, but the Debian
  package bundles AGPL-3+ licensed components, which is why this extension is
  hosted in the CNPG Extensions project rather than upstream.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
