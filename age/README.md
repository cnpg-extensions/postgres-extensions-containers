# Apache AGE
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[Apache AGE](https://age.apache.org/) is a PostgreSQL extension that provides graph database functionality, enabling you to store, query, and analyze graph data using Cypher queries alongside SQL. It is based on the openCypher graph query language.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### PostgreSQL compatibility

AGE 1.8.0 images using PGDG package revision `+2` require PostgreSQL 18.7
or later within major version 18. Upgrade PostgreSQL first: on 18.6, AGE
prevents startup with `undefined symbol: heap_datum_check`. CNPG does not
enforce extension minimum minor versions.

### 1. Add the age extension image to your Cluster

Define the `age` extension under the `postgresql.extensions` section of
your `Cluster` resource. Note that `age` must be added to
`shared_preload_libraries` for the extension to function. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-age
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - age
    extensions:
    - name: age
```

### 2. Enable the extension in a database

You can install `age` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-age-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-age
  extensions:
  - name: age
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION age;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `age` listed among the installed extensions.

## Known Caveats

- **`shared_preload_libraries` required**: Apache AGE must be listed in
  `shared_preload_libraries`. Without it, `CREATE EXTENSION age` will fail
  with a "must be preloaded" error.
- **License**: AGE itself is Apache-2.0, but its bundled CSV parser library
  (`libcsv`) is LGPL-2.1, which is why this extension is hosted in the
  CNPG Extensions project rather than upstream.
- **Cypher support**: After installation, use `SET search_path = ag_catalog, "$user", public;`
  to access AGE's graph functions and the `cypher()` function for graph queries.

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

All relevant license and copyright information for the `age` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
