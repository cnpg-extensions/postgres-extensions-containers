# Point cloud storage

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pgPointcloud adds PostgreSQL types and functions for storing, querying, and transforming LiDAR point-cloud data. Point formats and values live in database tables; the extension does not need to write container files. See the [upstream project](https://github.com/pgpointcloud/pointcloud) for the extension documentation.

This image supports PostgreSQL 18 on Debian Bookworm and Trixie. The selected PGDG package versions are maintained independently per suite in `metadata.hcl`.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Install with CloudNativePG

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pointcloud
spec:
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  instances: 1
  enableSuperuserAccess: true
  storage:
    size: 1Gi
  postgresql:
    extensions:
    - name: pointcloud
---
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pointcloud-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pointcloud
  extensions:
  - name: pointcloud
```

The PGDG package links to libxml2 and zlib. The optional `pointcloud_postgis` integration files are omitted because that feature requires a separately supplied PostGIS extension. The base pointcloud feature works without PostGIS.

### Register a point format and read a point

`pointcloud_formats` stores the schema used to decode each point. A database administrator registers a PCID once and grants the application role read access. Run the INSERT and GRANT below through the CNPG-managed PostgreSQL endpoint using the `cluster-pointcloud-superuser` Secret; applications can then run the SELECT as `app`. The Cluster example enables that administrator connection for setup.

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

GRANT SELECT ON pointcloud_formats TO app;

SELECT PC_Get(PC_MakePoint(1, ARRAY[-127, 45, 124.0, 4.0]), 'Intensity');
```

Schemas and point values live in PostgreSQL tables. No database pod shell or container filesystem changes are needed.


## Licenses and updates

The extension is licensed under `BSD-3-Clause`. Its copyright notice is included under `/licenses/<package>/`. The supported CNPG base images provide the runtime libraries required by the extension, so no files are staged under `/system`. The image includes no source archives. Renovate tracks the suite-specific PGDG package; rebuild against the supported Debian suite and review package and notice changes.
