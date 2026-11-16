# ogr_fdw

ogr_fdw exposes GDAL/OGR vector data sources as PostgreSQL foreign tables. See the [upstream ogr_fdw project](https://github.com/pramsey/pgsql-ogr-fdw) for supported options. It can read local files and remote datasets supported by the bundled GDAL build. It does not run an external GIS service.

PG18 packages are available for both Bookworm and Trixie on amd64 and arm64. The image sets GDAL_DATA to its bundled coordinate-system data directory and stages the linked GDAL runtime libraries.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the ogr-fdw extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-ogr-fdw
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: ogr-fdw
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION ogr_fdw;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

The catalog supplies `GDAL_DATA` and `PROJ_DATA`, with `${image_root}` expanded
to the extension mount directory for GDAL driver data and PROJ coordinate-system
data. Replace the example URL below with a reachable GeoJSON datasource containing
a layer named `places` and properties `place_id` and `name`. Application queries
remain on the managed PostgreSQL endpoint.

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

The suite-specific PGDG package versions and SQL version are recorded in
`metadata.hcl`. The extension is MIT-licensed. Copyright notices for bundled runtime packages and GDAL/PROJ data are under `/licenses/<package>/`. The image includes no source archives.

Renovate tracks both PGDG package versions. Rebuild after package or base-image security updates and review the resulting runtime libraries and package notices.
