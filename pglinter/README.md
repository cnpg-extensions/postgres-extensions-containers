# pglinter
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pglinter](https://github.com/pmpetit/pglinter) checks PostgreSQL databases for
schema design and configuration problems, including missing primary keys,
redundant indexes, and missing indexes on foreign keys. These images support
PostgreSQL 18 on Debian Bookworm and Trixie.

## Usage

### 1. Add the pglinter extension image to your Cluster

Define the `pglinter` extension under the `postgresql.extensions` section
of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pglinter
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pglinter
      image:
        reference: ghcr.io/cnpg-extensions/pglinter:2.0.0-18-trixie
```

### 2. Enable the extension in a database

You can install `pglinter` in a specific database by creating or updating
a `Database` resource, or by running `CREATE EXTENSION` directly in `psql`.
For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pglinter-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pglinter
  extensions:
  - name: pglinter
    version: '2.0.0'
```

Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pglinter;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
SELECT * FROM pglinter.get_violations();
```

The query returns findings from the enabled lint rules.

## Contributors

Maintained by Jeremy Schneider (@ardentperf).

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
