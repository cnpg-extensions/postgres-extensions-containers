# PL/R
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[PL/R](https://www.joeconway.com/plr/) is a PostgreSQL procedural language extension that enables writing database functions in R. It allows you to use R's statistical and data analysis capabilities directly within SQL queries.

## Usage

### 1. Add the plr extension image to your Cluster

Define the `plr` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-plr
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: plr
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-plr
        reference: ghcr.io/cnpg-extensions/plr:8.4.8.6-18-trixie
```

### 2. Enable the extension in a database

You can install `plr` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-plr-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-plr
  extensions:
  - name: plr
    # renovate: suite=trixie-pgdg depName=postgresql-18-plr extractVersion=^(?<version>\d+\.\d+\.\d+\.\d+)
    version: '8.4.8.6'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION plr;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `plr` listed among the installed extensions. You can then test R
integration:

```sql
SELECT plr_version();
```

## Known Caveats

- **R runtime bundled**: The full R runtime (`libR.so` and related libraries)
  is bundled in the image under `/system/`. Only the base R packages are
  available. Additional R packages cannot be installed at runtime in a minimal
  container environment.
- **Self-referential symlink fix**: The R library installs `libR.so` as a
  symlink pointing to itself via a complex chain. The Dockerfile includes a
  guard to avoid creating broken self-referential symlinks during the
  ldd-diff step.
- **Testing limitation**: The CI tests verify that the extension can be created
  (`CREATE EXTENSION plr`) and that the `plr_version()` function returns a
  result. Full R statistical function tests were not exercised.
- **License**: PL/R is GPL-2+, which is why it is hosted in the
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

All relevant license and copyright information for the `plr` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
