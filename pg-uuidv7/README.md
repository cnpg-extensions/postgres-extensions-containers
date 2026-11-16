# pg_uuidv7
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_uuidv7](https://github.com/fboulnois/pg_uuidv7) is a PostgreSQL extension that provides functions for generating and working with UUID version 7 (UUIDv7) identifiers. UUIDv7 is a time-sortable UUID format that embeds a Unix timestamp, making it more suitable than UUID v4 for use as database primary keys.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-uuidv7 extension image to your Cluster

Define the `pg-uuidv7` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-uuidv7
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pg-uuidv7
```

### 2. Enable the extension in a database

You can install `pg_uuidv7` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-uuidv7-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-uuidv7
  extensions:
  - name: pg_uuidv7
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_uuidv7;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_uuidv7` listed among the installed extensions. You can then
generate a UUIDv7 with:

```sql
SELECT uuid_generate_v7();
```

## Known Caveats

- **License**: `pg_uuidv7` is licensed under MPL-2.0 (Mozilla Public License),
  which is why it is hosted in the CNPG Extensions project rather than upstream.

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg-uuidv7` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
