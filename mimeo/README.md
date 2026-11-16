# Mimeo
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Specialized per-table replication using snapshot, incremental, and DML-based methods. [Upstream project](https://pgxn.org/dist/mimeo/1.5.1/doc/mimeo.html).

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-mimeo
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
    - name: mimeo
~~~

Install `dblink` and `mimeo` in the destination database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-mimeo-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-mimeo
  extensions:
  - name: dblink
  - name: mimeo
~~~

The `mimeo` control file requires `dblink`; install both extensions in the destination Database. By default, the PGDG SQL installs its objects in `public`, including `public.dblink_mapping_mimeo`, `public.table_maker`, and `public.refresh_table`. Store source credentials in the mapping table using appropriately restricted roles, and schedule refresh functions from a separate client. Mimeo copies selected tables, not a cluster or database catalog.

## Package and runtime details

PG18 images use the PGDG `postgresql-18-mimeo` package. Its full Debian copyright notice is carried in `/licenses/postgresql-18-mimeo/`. Requires the CNPG base-image `dblink` extension. Upstream recommends `pg_jobmon` for audit logging; it is optional.

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. Renovate tracks the PGDG package pins in `metadata.hcl`.

For this standalone setup, pass `p_jobmon := false` to `table_maker` and
`refresh_table`. Enable job logging only after separately provisioning the
optional `pg_jobmon` extension.
