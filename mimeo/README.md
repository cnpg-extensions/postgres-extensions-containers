# Mimeo
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Replicates individual tables between PostgreSQL databases using snapshot,
incremental, and DML-based methods. Use it to bring selected tables from
several databases together for reporting.

For more information, see the [upstream documentation](https://github.com/omniti-labs/mimeo).

## Dependencies and conflicts

Requires `dblink` in the same database.

### 1. Add the mimeo extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-mimeo
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: mimeo
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION IF NOT EXISTS dblink;
CREATE EXTENSION mimeo;
```

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT count(*) AS configured_replications FROM public.refresh_config;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
