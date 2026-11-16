# PgQ
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

A transactional, lockless event queue implemented with SQL and PostgreSQL C helpers. [Upstream project](https://github.com/pgq/pgq).

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgq
spec:
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    extensions:
    - name: pgq
~~~

Install the SQL extension in the Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgq-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgq
  extensions:
  - name: pgq
~~~

~~~sql
SELECT pgq.create_queue('order_events');
SELECT pgq.insert_event('order_events', 'order_created', 'order_id                                  ');
~~~

A separate `pgqd` daemon advances ticks and handles queue maintenance. The server image does not start or supervise daemon processes.

## Package and runtime details

PG18 images use the PGDG `postgresql-18-pgq3` package. Its full Debian copyright notice is carried in `/licenses/postgresql-18-pgq3/`. Server C helpers use libc/libpq from the base image. The PGQ tick/maintenance daemon is not bundled; run PGDG `pgqd` separately and connect through a CNPG `-rw` service.

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. Renovate tracks the PGDG package pins in `metadata.hcl`.
