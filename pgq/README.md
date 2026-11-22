# PgQ
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides a transactional event queue in PostgreSQL for applications that
process events asynchronously. For example, queue work when data changes so
another program can handle it later.

Run `pgqd` on a separate server and connect it to your CNPG primary to
advance queues and perform maintenance. This image supplies only the
database extension.

For more information, see the [upstream documentation](https://github.com/pgq/pgq).

### 1. Add the pgq extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgq
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pgq
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pgq;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

~~~sql
SELECT pgq.create_queue('order_events');
SELECT pgq.insert_event('order_events', 'order_created', 'order_id=42');
~~~

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
