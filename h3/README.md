# h3
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Binds the Uber H3 hierarchical hexagonal geospatial indexing system to
PostgreSQL. Use it to group and count locations on a map, such as delivery
stops in each area.

This image includes `h3` for working with map cells and the optional
`h3_postgis` extension for using those cells with PostGIS shapes and raster
data. Enable `h3_postgis` only if needed, after enabling `h3`, `postgis`, and
`postgis_raster`.

For more information, see the [upstream documentation](https://github.com/zachasme/h3-pg).

## Dependencies and conflicts

The optional `h3_postgis` extension requires `h3`, `postgis`, and
`postgis_raster` in the same database.

### 1. Add the h3 extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

Define the `h3` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-h3
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: postgis
    - name: h3
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_raster;
CREATE EXTENSION h3;
CREATE EXTENSION h3_postgis;
```

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT h3_get_extension_version();
SELECT h3_lat_lng_to_cell(ST_SetSRID(ST_Point(0, 0), 4326), 1);
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
