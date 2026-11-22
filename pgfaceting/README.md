# pgfaceting
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Uses Roaring bitmap indexes to compute fast facet counts for filtered
searches. Use it to show how many results match each filter option, such as
a size or color, as a search narrows.

For more information, see the [upstream documentation](https://github.com/cybertec-postgresql/pgfaceting).

## Dependencies and conflicts

Requires `roaringbitmap` in the same database.

### 1. Add the pgfaceting extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

Include both the `roaringbitmap` and `pgfaceting` extension images in your
Cluster, as shown below.

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

```sql
CREATE EXTENSION IF NOT EXISTS roaringbitmap;
CREATE EXTENSION pgfaceting;
```

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Create a facet definition for a `color` column:

```sql
SELECT * FROM faceting.plain_facet('color');
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
