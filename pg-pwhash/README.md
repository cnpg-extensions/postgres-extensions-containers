# Advanced password hashing

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Provides adaptive Argon2, scrypt, and yescrypt password-hashing functions.
Use it to store and check application passwords as hashes instead of saving
the passwords themselves.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/cybertec-postgresql/pg_pwhash).

### 1. Add the pg-pwhash extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-pwhash
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-pwhash
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pg_pwhash;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT pwhash_crypt('password', pwhash_gen_salt('argon2id'));
```

As with PostgreSQL's `crypt()`, verify a candidate password by passing the stored hash as the salt argument:

```sql
WITH credentials AS (
  SELECT pwhash_crypt('password', pwhash_gen_salt('argon2id')) AS stored_hash
)
SELECT pwhash_crypt('password', stored_hash) = stored_hash AS password_matches
FROM credentials;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
