# h3
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[h3-pg](https://github.com/zachasme/h3-pg) is a PostgreSQL extension that binds the [Uber H3](https://h3geo.org/) hierarchical hexagonal geospatial indexing system to PostgreSQL. It enables efficient geospatial analysis using H3 cell indexes.

## Usage

### 1. Add the h3 extension image to your Cluster

Define the `h3` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-h3
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: h3
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-h3
        reference: ghcr.io/cnpg-extensions/h3:4.2.3-18-trixie
```

### 2. Enable the extension in a database

You can install `h3` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-h3-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-h3
  extensions:
  - name: h3
    # renovate: suite=trixie-pgdg depName=postgresql-18-h3 extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '4.2.3'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION h3;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `h3` listed among the installed extensions.

## Known Caveats

- **Runtime library dependency**: This extension requires `libh3-1` at runtime.
  The library is bundled in the image under `/system/`. The `ld_library_path`
  is configured to include this directory automatically.
- **License**: The H3 library (`libh3`) itself is Apache-2.0, but the Debian
  package bundles AGPL-3+ licensed components, which is why this extension is
  hosted in the CNPG Extensions project rather than upstream.

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

All relevant license and copyright information for the `h3` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
