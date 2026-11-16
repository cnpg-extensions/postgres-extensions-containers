# pg-wait-sampling
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[`pg_wait_sampling`](https://github.com/postgrespro/pg_wait_sampling) samples PostgreSQL wait events and exposes current, historical, and aggregated profile views in SQL.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Usage

Add the extension image and preload its worker in a complete Cluster definition:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-wait-sampling
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
    - pg_wait_sampling
    extensions:
    - name: pg-wait-sampling
~~~

Install the extension in a database:

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-wait-sampling-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-wait-sampling
  extensions:
  - name: pg_wait_sampling
~~~

After the library is preloaded and the extension is installed, inspect sampled waits:

~~~sql
SELECT event_type, event, sum(count) AS samples
FROM pg_wait_sampling_profile
GROUP BY event_type, event
ORDER BY samples DESC;
~~~

## Supported matrix and licenses

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. The PostgreSQL license notice is included under `/licenses/postgresql-18-pg-wait-sampling/`. Renovate tracks the versioned PGDG package.
