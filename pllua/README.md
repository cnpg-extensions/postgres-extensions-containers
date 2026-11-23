# PL/Lua
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Lets you write PostgreSQL functions in Lua. Use it to process database
values with Lua, such as calculating a total whenever a row is saved.

This image includes four extensions you can enable separately.

The optional `hstore_pllua` and `hstore_plluau` helpers let each language work
with key/value pairs from `hstore`, which is included in the CNPG PostgreSQL
base image and must also be enabled to use these helpers.

For more information, see the [upstream documentation](https://pllua.github.io/pllua/).

> [!CAUTION]
> Use `pllua`, the trusted Lua language, for normal use. The untrusted `plluau`
> language can access files, run programs, and use the network as PostgreSQL’s
> operating-system user; reserve it for exceptional cases requiring that level
> of access.

## Dependencies and conflicts

The optional `hstore_pllua` and `hstore_plluau` extensions require `hstore`
and their matching Lua language in the same database.

### 1. Add the pllua extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

Mount the image into your Cluster:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pllua
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pllua
```

### 2. Enable the extension in a database

```sql
CREATE EXTENSION IF NOT EXISTS hstore;
CREATE EXTENSION pllua;
CREATE EXTENSION hstore_pllua;
```

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
CREATE FUNCTION lua_value(value hstore) RETURNS text
LANGUAGE pllua AS $$ return value.example $$;
SELECT lua_value('example=>ok'::hstore); -- ok
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
