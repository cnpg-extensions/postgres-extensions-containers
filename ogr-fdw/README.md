# ogr_fdw

Makes geographic data from other sources available as PostgreSQL tables.
Use it to query online map data alongside records already in your database.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

The image includes tools for reading geographic data, but no maps or datasets.
Data sources must be remote and reachable from your database, such as a GeoJSON
file served over HTTPS.

For more information, see the [upstream documentation](https://github.com/pramsey/pgsql-ogr-fdw).

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

This example reads geographic data from a URL as a table. Replace the URL
with a GeoJSON source your database can reach, with a layer named `places`
and fields named `place_id` and `name`.

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

Supported data formats depend on the GDAL version available from the
PostgreSQL package repository (PGDG).

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
