# pg-repack
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[`pg_repack`](https://github.com/reorg/pg_repack) rebuilds tables and indexes while allowing normal reads and writes. The server image provides the PostgreSQL extension library and SQL objects. The `pg_repack` client is run separately and must match the server's PostgreSQL major and extension version.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the server image to a complete Cluster definition:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-repack
spec:
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  enableSuperuserAccess: true
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    extensions:
    - name: pg-repack
~~~

Install the server extension in the database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-repack-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-repack
  extensions:
  - name: pg_repack
~~~

Run a matching client from a separate job, host, or maintenance image. On a Debian Trixie PostgreSQL 18 client, install the PGDG `postgresql-18-repack` package and connect through the Cluster's managed `-rw` service:

~~~sh
pg_repack --host=cluster-pg-repack-rw --username=postgres --dbname=app --table=public.large_table
~~~

Supply credentials through a Kubernetes Secret or the client environment. The extension image deliberately does not put the client executable in the PostgreSQL server image.

## Supported matrix and licenses

The server image supports PostgreSQL 18 on Debian Bookworm and Trixie. Package copyright (BSD-3-Clause) is included under `/licenses/postgresql-18-repack/`. The separate client must use the same upstream version; Renovate tracks PGDG package versions.
