# pgAgent
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pgAgent](https://www.pgadmin.org/docs/pgadmin4/latest/pgagent.html) is a PostgreSQL job scheduling agent that enables you to schedule SQL scripts, shell commands, and batch jobs to run at specified intervals. It consists of a PostgreSQL extension (for storing job definitions) and a separate daemon process (`pgagent`) that executes scheduled jobs.

## Usage

### 1. Add the pgagent extension image to your Cluster

Define the `pgagent` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgagent
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pgagent
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pgagent
        reference: ghcr.io/cnpg-extensions/pgagent:4.2.3-18-trixie
```

### 2. Enable the extension in a database

You can install `pgagent` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgagent-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgagent
  extensions:
  - name: pgagent
    # renovate: suite=trixie-pgdg depName=postgresql-18-pgagent extractVersion=^(?<version>\d+\.\d+)
    version: '4.2'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pgagent;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pgagent` listed among the installed extensions.

## Known Caveats

- **Daemon required**: The `pgagent` extension only stores job definitions in
  the database. To actually execute jobs, you must run the `pgagent` daemon
  process separately. The daemon binary is included in the image under `/bin/`
  and is added to PATH automatically by the CNPG operator. However, running the
  daemon as a sidecar or separate process requires additional configuration
  outside the scope of this image.
- **Testing limitation**: The CI tests verify that the extension can be created
  (`CREATE EXTENSION pgagent`), but do not test the actual job scheduling
  daemon or job execution.
- **License**: `pgagent` itself is PostgreSQL-licensed, but its runtime
  dependency on Boost libraries is BSL-1.0 (Business Source License), which is
  why this extension is hosted in the CNPG Extensions project rather than
  upstream.

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

All relevant license and copyright information for the `pgagent` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
