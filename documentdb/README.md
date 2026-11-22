# DocumentDB
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides a MongoDB-compatible document database built on PostgreSQL.
Supports the MongoDB wire protocol, so existing MongoDB drivers and tools can
query BSON documents.

The image includes `documentdb_core` for BSON types, `documentdb` for the
document and collection APIs, and `documentdb_extended_rum` for BSON indexes.

For more information, see the [project website](https://documentdb.io/) and
the [upstream getting started guide](https://documentdb.io/docs/getting-started/).

> [!NOTE]
> For **SQL-only use**, add DocumentDB from the CNPG extension catalog. You can
> query it directly through PostgreSQL without installing a gateway.
>
> The gateway lets a MongoDB client such as `mongosh` connect to DocumentDB.
> Deploying the gateway with this extension image is an advanced use case for
> teams that want to manage the CNPG `Cluster` themselves, for example to run
> DocumentDB alongside other PostgreSQL workloads.
>
> For most users who want a **MongoDB-compatible service** on Kubernetes, the
> simplest path is the [DocumentDB Kubernetes Operator](https://documentdb.io/docs/kubernetes-operator/).
> You define a `DocumentDB` resource, and the operator provisions a dedicated
> CNPG cluster for it and configures the gateway.

## Dependencies and conflicts

For standalone SQL-only use, specify just `- name: documentdb` for the DocumentDB
entry in `spec.postgresql.extensions`. Omit the image pin and `ld_library_path`.
CNPG gets both from the catalog and picks up new image versions automatically
when the catalog is refreshed.

For a gateway deployment, first choose the exact upstream DocumentDB release.
Identify the extension and gateway builds for that release and pin both images
by digest in the Cluster manifest.

DocumentDB requires `pg_cron`, `vector`, `postgis`, `tsm_system_rows`, and
`documentdb_core`. The PostgreSQL base image supplies `tsm_system_rows`.
The example also enables RUM and the bundled extended-RUM access method.

### 1. Add the documentdb extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For SQL-only use, omit `pg_hba` and `plugins`.
The gateway connects to the `postgres` database. The loopback rules below allow
any process in the pod to connect there as `documentdb` or a member of
`documentdb_socket_users` without a password.

For a gateway deployment, install the DocumentDB CNPG-I sidecar injector as a
separate Deployment in the CNPG operator’s namespace before enabling it in the
Cluster’s `spec.plugins`.
CNPG then asks the injector to add the gateway container to each PostgreSQL pod.
See the upstream
[sidecar injector guide](https://github.com/documentdb/documentdb-kubernetes-operator/blob/1.2.0/docs/developer-guides/sidecar-injector-plugin-configuration.md)
and [TLS guide](https://github.com/documentdb/documentdb-kubernetes-operator/blob/1.2.0/docs/operator-public-documentation/v1/configuration/tls.md).

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-documentdb
spec:
  instances: 1
  storage:
    size: 1Gi
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  postgresql:
    pg_ident:
    - local postgres +documentdb_socket_users
    pg_hba:
    - host postgres documentdb,+documentdb_socket_users 127.0.0.1/32 trust
    - host postgres documentdb,+documentdb_socket_users ::1/128 trust
    extensions:
    - name: pg-cron
    - name: pgvector
    - name: postgis
    - name: rum
    - name: documentdb
      ld_library_path: [lib]
      image:
        reference: ghcr.io/cnpg-extensions/documentdb:1.2-18-trixie@sha256:DOCUMENTDB_DIGEST
    shared_preload_libraries:
    - pg_cron
    - pg_documentdb_core
    - pg_documentdb
    - pg_documentdb_extended_rum
    parameters:
      cron.database_name: postgres
      documentdb.localhost_connection_string: host=/controller/run
  plugins:
  - name: cnpg-i-sidecar-injector.documentdb.io
    parameters:
      gatewayImage: ghcr.io/documentdb/documentdb-kubernetes-operator/gateway:1.0.1@sha256:502b4e7bfcbb926597a9f9d4a2a6dc8174ff502fbcf72cdb9e4c1a3b2d58a41e
      gatewayTLSSecret: documentdb-gateway-tls
```

### 2. Enable the extension in a database

Run the following SQL as an administrator in `postgres` for the gateway or in
`app` for the SQL-only example.

```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS tsm_system_rows;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS rum WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS documentdb_core;
CREATE EXTENSION documentdb;
CREATE EXTENSION documentdb_extended_rum WITH SCHEMA public;
```

Create the socket group and a dedicated DocumentDB administrator login:

```sql
CREATE ROLE documentdb_socket_users NOLOGIN;
CREATE ROLE documentdb_admin LOGIN;
GRANT documentdb_socket_users TO documentdb_admin;
GRANT documentdb_admin_role TO documentdb_admin;
```

In `psql`, use `\password documentdb_admin` to set the login's password.

For each additional application login that needs local reconnections, grant it
`documentdb_socket_users`. Grant its DocumentDB permissions separately. Consider
cluster-wide privileges when choosing a role. For example,
`documentdb_readonly_role` inherits PostgreSQL's `pg_read_all_data`.

### 3. Verify installation

For the SQL-only setup, connect to the `app` database as `documentdb_admin`. List the document databases
using a BSON command, then check that PostgreSQL registered the extended-RUM
index access method. Expect `true` and `documentdb_extended_rum`, respectively.

```sql
SELECT documentdb_api.list_databases('{"listDatabases":1}'::documentdb_core.bson) IS NOT NULL AS api_ready;
SELECT amname FROM pg_catalog.pg_am WHERE amname = 'documentdb_extended_rum';
```

To verify a running gateway, use its Service hostname, CA certificate, and
login. This example connects from the same namespace as the Service and
prompts for the password.

```sh
mongosh 'mongodb://documentdb-gateway:10260/catalog?authSource=admin&directConnection=true' \
  --tls --tlsCAFile ca.crt --username mongo_admin
```

In `mongosh`, write a document and read it back. Expect the returned document
to contain `ready: true`.

```javascript
db.items.updateOne({ _id: "gateway-check" }, { $set: { ready: true } }, { upsert: true })
db.items.findOne({ _id: "gateway-check" })
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
