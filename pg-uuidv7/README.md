# pg_uuidv7
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_uuidv7](https://github.com/fboulnois/pg_uuidv7) is a PostgreSQL extension that provides functions for generating and working with UUID version 7 (UUIDv7) identifiers. UUIDv7 is a time-sortable UUID format that embeds a Unix timestamp, making it more suitable than UUID v4 for use as database primary keys.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-uuidv7 extension image to your Cluster

Define the `pg-uuidv7` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-uuidv7
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-uuidv7
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_uuidv7;` in the target database.

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

You should see `pg_uuidv7` listed among the installed extensions. You can then
generate a UUIDv7 with:

```sql
SELECT uuid_generate_v7();
```

## Known Caveats

- **License**: `pg_uuidv7` is licensed under MPL-2.0 (Mozilla Public License),
  which is why it is hosted in the CNPG Extensions project rather than upstream.

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg-uuidv7` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
