# plprofiler
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[plprofiler](https://github.com/bigsql/plprofiler) is a PostgreSQL extension that provides execution profiling for PL/pgSQL functions and procedures. It collects per-statement call counts, total execution time, and self-time, helping you identify performance bottlenecks in stored procedure code.

## Usage

### 1. Add the plprofiler extension image to your Cluster

Define the `plprofiler` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-plprofiler
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: plprofiler
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-plprofiler
        reference: ghcr.io/cnpg-extensions/plprofiler:4.2.5-18-trixie
```

### 2. Enable the extension in a database

You can install `plprofiler` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-plprofiler-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-plprofiler
  extensions:
  - name: plprofiler
    # renovate: suite=trixie-pgdg depName=postgresql-18-plprofiler extractVersion=^(?<version>\d+\.\d+)
    version: '4.2'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION plprofiler;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `plprofiler` listed among the installed extensions.

## Known Caveats

- **License**: `plprofiler` is Artistic-2.0, which is why it is hosted in the
  CNPG Extensions project rather than upstream.

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

All relevant license and copyright information for the `plprofiler` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
