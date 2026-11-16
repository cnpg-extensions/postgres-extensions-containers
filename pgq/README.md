# PgQ
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

A transactional, lockless event queue implemented with SQL and PostgreSQL C helpers. [Upstream project](https://github.com/pgq/pgq).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pgq extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgq
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pgq
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pgq;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

~~~sql
SELECT pgq.create_queue('order_events');
SELECT pgq.insert_event('order_events', 'order_created', 'order_id                                  ');
~~~

A separate `pgqd` daemon advances ticks and handles queue maintenance. The server image does not start or supervise daemon processes.

## Package and runtime details

PG18 images use the PGDG `postgresql-18-pgq3` package. Its full Debian copyright notice is carried in `/licenses/postgresql-18-pgq3/`. Server C helpers use libc/libpq from the base image. The PGQ tick/maintenance daemon is not bundled; run PGDG `pgqd` separately and connect through a CNPG `-rw` service.

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. Renovate tracks the PGDG package pins in `metadata.hcl`.
