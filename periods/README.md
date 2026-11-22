# periods

Adds SQL periods and system versioning to PostgreSQL so you can track
changes to rows over time. Use it to look up earlier versions of records,
such as their values before the last update.

For more information, see the [upstream documentation](https://github.com/xocolatl/periods).

## Dependencies and conflicts

Requires `btree_gist` in the same database.

### 1. Add the periods extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-periods
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: periods
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION periods;
```

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT * FROM periods.periods;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
