# MobilityDB
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds support for temporal and spatio-temporal data types. Use it to track
where something was at a particular time, such as a vehicle along its route.
MobilityDB extends PostGIS with temporal types for geographic data.

This image includes `mobilitydb` for working with data that changes over time
and the optional `mobilitydb_datagen` extension for creating random test data.
Enable `mobilitydb_datagen` only if needed, after enabling `mobilitydb`.

For more information, see the [upstream documentation](https://mobilitydb.com/).

## Dependencies and conflicts

Requires `postgis`. The optional `mobilitydb_datagen` extension requires
`mobilitydb` in the same database.

### 1. Add the mobilitydb extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

Include both the `postgis` and `mobilitydb` extension images in your Cluster,
as shown below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-mobilitydb
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: postgis
    - name: mobilitydb
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION mobilitydb;
CREATE EXTENSION mobilitydb_datagen;
```

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT mobilitydb_version();
SELECT random_int(1, 10);
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
