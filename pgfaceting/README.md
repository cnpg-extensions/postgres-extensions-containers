# pgfaceting
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pgfaceting uses Roaring bitmap indexes to compute fast facet counts for filtered
searches.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

### 1. Add the pgfaceting extension image to your Cluster

Include the required `roaringbitmap` extension image before `pgfaceting`.
No shared preload configuration is needed.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgfaceting
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: roaringbitmap
    - name: pgfaceting
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pgfaceting;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

Install `roaringbitmap`, then `pgfaceting` in that order. Through SQL, run
`CREATE EXTENSION roaringbitmap;` before `CREATE EXTENSION pgfaceting;`.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx pgfaceting
```

You should see `pgfaceting` listed with its installed SQL version.

## Use and maintain facets

After installing both extensions, use an administrator connection to the `app`
database to grant the table owner access to the schema and metadata tables:

```sql
GRANT USAGE ON SCHEMA faceting TO app;
GRANT SELECT, INSERT, UPDATE, DELETE
  ON faceting.faceted_table, faceting.facet_definition TO app;
```

These grants permit management of the shared facet metadata; reserve them for
trusted table owners. Then connect to `app` as its owner:

```sql
CREATE TABLE items (id integer PRIMARY KEY, color text, size text);
INSERT INTO items VALUES (1, 'red', 'small'), (2, 'red', 'large'), (3, 'blue', 'small');
SELECT faceting.add_faceting_to_table('items', key => 'id',
  facets => ARRAY[faceting.plain_facet('color'), faceting.plain_facet('size')]);
SELECT * FROM faceting.count_results('items'::regclass,
  filters => ARRAY[ROW('color', 'red')]::faceting.facet_filter[]);
-- size=small: 1; size=large: 1
UPDATE items SET color = 'blue' WHERE id = 2;
SELECT faceting.merge_deltas('items'::regclass);
SELECT * FROM faceting.top_values('items'::regclass, n => 10);
-- color=blue: 2; color=red: 1
```

Facet indexes and pending changes are ordinary database tables, included in
normal database backup/replication. Schedule `CALL faceting.run_maintenance()`
through your SQL scheduler to merge deltas regularly. Keys must fit in 32-bit
integers. No external daemon or writable extension-image directory is needed.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
