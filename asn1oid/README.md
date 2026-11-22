# asn1oid
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Adds an ASN.1 object identifier type so you can store and compare hierarchical
identifiers in PostgreSQL. Use it to sort dotted identifiers such as `1.3.6.1`
by their numbered parts.

For more information, see the [upstream documentation](https://github.com/df7cb/pgsql-asn1oid).

### 1. Add the asn1oid extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-asn1oid
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: asn1oid
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION asn1oid;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

A SQL check that exercises the installed extension is:

```sql
SELECT '2.16.840.1.101.3.4.2.1'::asn1oid::text = '2.16.840.1.101.3.4.2.1';
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
