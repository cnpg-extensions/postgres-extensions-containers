# Apache AGE
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[Apache AGE](https://age.apache.org/) is a PostgreSQL extension that provides graph database functionality, enabling you to store, query, and analyze graph data using Cypher queries alongside SQL. It is based on the openCypher graph query language.

## Usage

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
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
      - "age"

    extensions:
    - name: age
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-age
        reference: ghcr.io/cnpg-extensions/age:1.8.0-18-trixie
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
    # renovate: suite=trixie-pgdg depName=postgresql-18-age extractVersion=^(?<version>[\d.]+)
    version: '1.8.0'
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
