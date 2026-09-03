# pg_rrule
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_rrule](https://github.com/petropavel13/pg_rrule) is a PostgreSQL extension that adds support for iCalendar recurrence rules (RRULE) as a native data type. It allows you to store and process recurring event schedules using the standard RFC 5545 iCalendar format.

## Usage

### 1. Add the pg-rrule extension image to your Cluster

Define the `pg-rrule` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-rrule
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg-rrule
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pg-rrule
        reference: ghcr.io/cnpg-extensions/pg-rrule:0.3.0-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_rrule` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-rrule-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-rrule
  extensions:
  - name: pg-rrule
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg-rrule extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '0.3.0'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_rrule;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_rrule` listed among the installed extensions.

## Known Caveats

- **Runtime library dependency**: This extension requires `libical3` at runtime.
  The library is bundled in the image under `/system/`.
- **License**: `pg_rrule` itself is MIT, but its runtime dependency `libical3`
  is dual-licensed under LGPL-2.1 or MPL-2.0, which is why this extension is
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

All relevant license and copyright information for the `pg-rrule` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
