# pg_rrule
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_rrule](https://github.com/petropavel13/pg_rrule) is a PostgreSQL extension that adds support for iCalendar recurrence rules (RRULE) as a native data type. It allows you to store and process recurring event schedules using the standard RFC 5545 iCalendar format.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-rrule extension image to your Cluster

Define the `pg-rrule` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-rrule
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-rrule
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_rrule;` in the target database.

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

You should see `pg_rrule` listed among the installed extensions.

## Known Caveats

- **Runtime library dependency**: This extension requires `libical3` at runtime.
  The library is bundled in the image under `/system/`.
- **License**: `pg_rrule` itself is MIT, but its runtime dependency `libical3`
  is dual-licensed under LGPL-2.1 or MPL-2.0, which is why this extension is
  hosted in the CNPG Extensions project rather than upstream.

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg-rrule` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
