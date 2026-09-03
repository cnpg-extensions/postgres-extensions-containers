# pldebugger
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pldebugger](https://github.com/EnterpriseDB/pldebugger) is a PostgreSQL extension that provides a server-side debugger for PL/pgSQL functions and procedures. It enables step-by-step debugging, breakpoints, and variable inspection for stored procedures, and is supported by tools such as pgAdmin.

## Usage

### 1. Add the pldebugger extension image to your Cluster

Define the `pldebugger` extension under the `postgresql.extensions` section of
your `Cluster` resource. Note that `plugin_debugger` must be added to
`shared_preload_libraries`. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pldebugger
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
      - "plugin_debugger"

    extensions:
    - name: pldebugger
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pldebugger
        reference: ghcr.io/cnpg-extensions/pldebugger:1.10-18-trixie
```

### 2. Enable the extension in a database

You can install `pldbgapi` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pldebugger-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pldebugger
  extensions:
  - name: pldebugger
    # renovate: suite=trixie-pgdg depName=postgresql-18-pldebugger extractVersion=^(?<version>\d+\.\d+)
    version: '1.1'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pldbgapi;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pldbgapi` listed among the installed extensions.

## Known Caveats

- **`shared_preload_libraries` required**: The `plugin_debugger` shared library
  must be listed in `shared_preload_libraries`. Without it, `CREATE EXTENSION
  pldbgapi` will fail.
- **SQL extension name differs from image name**: The extension image is named
  `pldebugger` but the PostgreSQL extension object is `pldbgapi`. Use
  `CREATE EXTENSION pldbgapi` (not `pldebugger`).
- **License**: `pldebugger` is Artistic-2.0, which is why it is hosted in the
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

All relevant license and copyright information for the `pldebugger` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
