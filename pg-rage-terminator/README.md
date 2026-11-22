# pg_rage_terminator
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Runs a background worker that can terminate random PostgreSQL sessions for
chaos testing. Use it in a test environment to check whether your application
recovers when database connections suddenly disappear.

`pg_rage_terminator` is a background worker with no SQL extension object;
no `CREATE EXTENSION` command is needed.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/disco-stu/pg_rage_terminator).

### 1. Add the pg-rage-terminator extension image to your Cluster

This extension requires `pg_rage_terminator` in `shared_preload_libraries`,
as shown below. Keep `pg_rage_terminator.chance: "0"` for this installation
check so the worker does not terminate sessions.

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

### 2. Verify installation

The safe `chance=0` default leaves all sessions alone while confirming the module loaded. A positive chance can terminate any randomly selected TCP-backed session visible to the worker; the extension has no database, role, or application allowlist. Use a positive value only in an isolated ephemeral chaos-test Cluster with no unrelated TCP clients. This component is not a SQL `CREATE EXTENSION` object; check its live setting with `SHOW pg_rage_terminator.chance` through the Cluster's managed PostgreSQL service.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
