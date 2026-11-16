# pg_cron
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_cron](https://github.com/citusdata/pg_cron) is an open-source extension
that provides a simple cron-based job scheduler for PostgreSQL, allowing you
to schedule PostgreSQL commands directly from the database.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### PostgreSQL compatibility

pg_cron 1.6.8 images using PGDG package revision `+3` require PostgreSQL 18.7
or later within major version 18. Upgrade PostgreSQL first: on 18.6, pg_cron
prevents startup with `undefined symbol: heap_datum_check`. CNPG does not
enforce extension minimum minor versions.

### 1. Add the cron extension image to your Cluster

Define the `pg-cron` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-cron
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      cron.database_name: app
      cron.use_background_workers: 'on'
    shared_preload_libraries:
    - pg_cron
    extensions:
    - name: pg-cron
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_cron;` in the target database.

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

You should see `pg_cron` listed among the installed extensions.

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg_cron` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
