# unit
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides SI unit values, conversions and arithmetic. For example, add
measurements recorded in meters and feet without doing the conversions
yourself.

For more information, see the [upstream documentation](https://github.com/df7cb/postgresql-unit).

## Dependencies and conflicts

Requires `plpgsql`, which is normally enabled by default.

### 1. Add the unit extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

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
