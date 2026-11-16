# PoWA server
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

PostgreSQL Workload Analyzer server-side history and snapshot schema. [Upstream project](https://powa.readthedocs.io/en/stable/).

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Create a dedicated PoWA Database and declare its required extensions:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-powa
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
    shared_preload_libraries:
    - pg_stat_statements
    - powa
    extensions:
    - name: powa
~~~

Install PoWA and its base-image dependencies in a Database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-powa-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-powa
  extensions:
  - name: pg_stat_statements
  - name: btree_gist
  - name: powa
~~~

Install `pg_stat_statements` and `btree_gist` in that Database as well. Start the separate PoWA collector/archivist only after server-side snapshots are configured. Use `powa_take_snapshot()` for a manual one-shot snapshot.

## Package and runtime details

PG18 images use the PGDG `postgresql-18-powa` package. The image carries the `powa.so` server module, its PostgreSQL LLVM bitcode, SQL/control files, and the full Debian copyright notice under `/licenses/postgresql-18-powa/`. The module's only external runtime dependency is libc from the CNPG base image. PoWA requires the base-image `pg_stat_statements` and `btree_gist` extensions. Its background worker is provided by `powa.so`; a separate PoWA collector/archivist and web UI are optional client components.

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. Renovate tracks the PGDG package pins in `metadata.hcl`.
