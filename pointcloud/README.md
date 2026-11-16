# Point cloud storage

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pgPointcloud adds PostgreSQL types and functions for storing, querying, and transforming LiDAR point-cloud data. Point formats and values live in database tables; the extension does not need to write container files. See the [upstream project](https://github.com/pgpointcloud/pointcloud) for the extension documentation.

This image supports PostgreSQL 18 on Debian Bookworm and Trixie. The selected PGDG package versions are maintained independently per suite in `metadata.hcl`.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pointcloud extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pointcloud
spec:
  imageCatalogRef: ...
  enableSuperuserAccess: true
  postgresql:
    extensions:
    - name: pointcloud
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pointcloud;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

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
