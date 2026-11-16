# ogr_fdw

ogr_fdw exposes GDAL/OGR vector data sources as PostgreSQL foreign tables. See the [upstream ogr_fdw project](https://github.com/pramsey/pgsql-ogr-fdw) for supported options. It can read local files and remote datasets supported by the bundled GDAL build. It does not run an external GIS service.

PG18 packages are available for both Bookworm and Trixie on amd64 and arm64. The image sets GDAL_DATA to its bundled coordinate-system data directory and stages the linked GDAL runtime libraries.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Install and read a GeoJSON layer

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-ogr-fdw
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
    - name: ogr-fdw
---
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-ogr-fdw-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-ogr-fdw
  extensions:
  - name: ogr_fdw
~~~

The catalog supplies `GDAL_DATA` and `PROJ_DATA`, with `${image_root}` expanded
to the extension mount directory for GDAL driver data and PROJ coordinate-system
data. The example below reads a GeoJSON file over HTTP; application queries remain on the managed PostgreSQL endpoint.

~~~sql
CREATE SERVER geojson_source
  FOREIGN DATA WRAPPER ogr_fdw
  OPTIONS (
    datasource 'https://data.example.net/places.geojson',
    format 'GeoJSON'
  );

CREATE FOREIGN TABLE places (
  place_id integer,
  name text
)
SERVER geojson_source
OPTIONS (layer 'places');

SELECT place_id, name
FROM places
ORDER BY place_id;
~~~

OGR_FDW only supports the GDAL drivers available in the installed libgdal build. The runtime includes GDAL's data files; place datasets in separately managed object storage or another supported datasource.

## Package, licensing and updates

Bookworm package: 1.1.9-1.pgdg12+1. Trixie package: 1.1.9-1.pgdg13+1. SQL version: 1.1. The extension is MIT-licensed. Copyright notices for bundled runtime packages and GDAL/PROJ data are under `/licenses/<package>/`. The image includes no source archives.

Renovate tracks both PGDG package versions. Rebuild after package or base-image security updates and review the resulting runtime libraries and package notices.
