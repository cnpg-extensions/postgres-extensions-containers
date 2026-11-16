# pgfaceting

Fast facet counts using roaring bitmap indexes. [Upstream documentation](https://github.com/cybertec-postgresql/pgfaceting).

## Supported images

PostgreSQL 18 on Debian Bookworm and Trixie, for amd64 and arm64.

## Declarative setup

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgfaceting
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
    - name: roaringbitmap
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-roaringbitmap
        reference: ghcr.io/cnpg-extensions/roaringbitmap:1.2.0-18-trixie
    - name: pgfaceting
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pgfaceting
        reference: ghcr.io/cnpg-extensions/pgfaceting:0.2.0-18-trixie
---
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgfaceting-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgfaceting
  extensions:
  - name: roaringbitmap
  - name: pgfaceting
    # renovate: suite=trixie-pgdg depName=postgresql-18-pgfaceting extractVersion=^(?<version>\d+\.\d+\.\d+)-
    version: '0.2.0'
```

For Bookworm, use the `postgresql-minimal-bookworm` catalog and the corresponding
`-18-bookworm` extension image tags. No shared preload configuration is needed.

## Use and maintain facets

Mount and install `roaringbitmap` first, as above. CNPG installs the extension
as an administrator. In the `app` database, grant the table owner access to
its schema and metadata tables before using it:

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

## Licensing and payload

The PGDG copyright file calls its license **Aasma**; the complete text is the
standard **BSD-3-Clause** license (including the non-endorsement clause), so
`metadata.hcl` uses that SPDX identifier. The shared SBOM generator retains
Debian's `LicenseRef-Aasma` label; it refers to the same reviewed license text.
The unmodified notice is shipped at
`/licenses/postgresql-18-pgfaceting/copyright`.

The image contains only pgfaceting SQL/control files and its copyright notice;
no shared libraries, interpreter or build tools are shipped. The required
roaringbitmap extension is a separate image with its own notices and SBOM.
Both fit the top-level README's CNCF-compatible declared-license group.

## Updates and validation

Renovate tracks both Debian package pins and the documented image tags. SQL
versions are extracted from the verified package version shape; review the
packaged control files and upgrade scripts when that shape changes. Rebuild
and validate both distributions and architectures after package updates.

The extension-specific Chainsaw test exercises real behavior through the mounted
image, in addition to the shared installation checks. Run:

```sh
task checks TARGET=pgfaceting
task e2e:test:full TARGET=pgfaceting
```

Maintained by the repository maintainers.
