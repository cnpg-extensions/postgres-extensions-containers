# pg_rage_terminator
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

A PostgreSQL background worker that can terminate random sessions for chaos testing. [Upstream project](https://github.com/disco-stu/pg_rage_terminator).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pg-rage-terminator extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-rage-terminator
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pg_rage_terminator
    parameters:
      pg_rage_terminator.chance: '0'
    extensions:
    - name: pg-rage-terminator
```

### 2. Database setup

`pg_rage_terminator` is a background worker and has no SQL extension object to
install. Create the application database through your usual database provisioning
process; no `CREATE EXTENSION` command is needed for this worker.

### 3. Verify operation

The safe `chance=0` default leaves all sessions alone while confirming the module loaded. A positive chance can terminate any randomly selected TCP-backed session visible to the worker; the extension has no database, role, or application allowlist. Use a positive value only in an isolated ephemeral chaos-test Cluster with no unrelated TCP clients. This component is not a SQL `CREATE EXTENSION` object; check its live setting with `SHOW pg_rage_terminator.chance` through the Cluster's managed PostgreSQL service.

## Package and runtime details

PG18 images use the PGDG `pg-rage-terminator-18` package. Its full Debian copyright notice is carried in `/licenses/pg-rage-terminator-18/`. C module depends on libc from the CNPG base image. No additional library is bundled. Upstream component source is PGDG `pg-rage-terminator`.

The image supports PostgreSQL 18 on Debian Bookworm and Trixie. Renovate tracks the PGDG package pins in `metadata.hcl`.
