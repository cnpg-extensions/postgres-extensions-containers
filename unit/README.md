# unit
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides SI unit values, conversions and arithmetic. Use it to add measurements
recorded in meters and feet without doing the conversions yourself.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

## Dependencies and conflicts

Requires `plpgsql`, which is normally enabled by default.

For more information, see the [upstream documentation](https://github.com/df7cb/postgresql-unit).

### 1. Add the unit extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-unit
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: unit
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION IF NOT EXISTS plpgsql;
CREATE EXTENSION unit;
```

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

A SQL check that exercises the installed extension is:

```sql
SELECT '1 m'::unit = '100 cm'::unit;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
