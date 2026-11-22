# Point cloud storage

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds PostgreSQL types and functions for storing, querying, and transforming
LiDAR point-cloud data. Use it to store and examine collections of measured
points in space, such as laser scans of buildings or terrain.

This image includes `pointcloud` for storing point clouds and the optional
`pointcloud_postgis` extension for using them with PostGIS shapes. Enable
`pointcloud_postgis` after enabling both `postgis` and `pointcloud`, as shown
below.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

## Dependencies and conflicts

The optional `pointcloud_postgis` extension requires `pointcloud` and
`postgis` in the same database.

For more information, see the [upstream documentation](https://github.com/pgpointcloud/pointcloud).

### 1. Add the pointcloud extension image to your Cluster

This example uses both the `postgis` and `pointcloud` extension images.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pointcloud
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: postgis
    - name: pointcloud
```

### 2. Enable the extension in a database

Enable the extensions in the same database:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION pointcloud;
CREATE EXTENSION pointcloud_postgis;
```

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

As an administrator, register a point format, then turn a sample point into a
PostGIS geometry. Run this example in a database where PCID `1` is unused.

```sql
INSERT INTO pointcloud_formats (pcid, srid, schema) VALUES (1, 4326,
$schema$
<pc:PointCloudSchema xmlns:pc="http://pointcloud.org/schemas/PC/1.1">
  <pc:dimension><pc:position>1</pc:position><pc:size>4</pc:size><pc:name>X</pc:name><pc:interpretation>int32_t</pc:interpretation><pc:scale>0.01</pc:scale></pc:dimension>
  <pc:dimension><pc:position>2</pc:position><pc:size>4</pc:size><pc:name>Y</pc:name><pc:interpretation>int32_t</pc:interpretation><pc:scale>0.01</pc:scale></pc:dimension>
  <pc:dimension><pc:position>3</pc:position><pc:size>4</pc:size><pc:name>Z</pc:name><pc:interpretation>int32_t</pc:interpretation><pc:scale>0.01</pc:scale></pc:dimension>
  <pc:dimension><pc:position>4</pc:position><pc:size>2</pc:size><pc:name>Intensity</pc:name><pc:interpretation>uint16_t</pc:interpretation><pc:scale>1</pc:scale></pc:dimension>
  <pc:metadata><Metadata name="compression">dimensional</Metadata></pc:metadata>
</pc:PointCloudSchema>
$schema$);

SELECT ST_AsEWKT(PC_MakePoint(1, ARRAY[-127, 45, 124.0, 4.0])::geometry);
-- SRID=4326;POINT(-127 45 124)
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
