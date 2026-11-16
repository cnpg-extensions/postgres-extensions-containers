# HTTP requests from PostgreSQL

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

http adds HTTP client functions to PostgreSQL so SQL can call HTTP services through libcurl. See the [upstream project](https://github.com/pramsey/pgsql-http) for the extension documentation.

This image supports PostgreSQL 18 on Debian Bookworm and Trixie. The selected PGDG package versions are maintained independently per suite in `metadata.hcl`.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Install with CloudNativePG

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-http
spec:
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    extensions:
    - name: http
---
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-http-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-http
  extensions:
  - name: http
```

The PGDG package links to libcurl. The build stages the resolved non-core shared libraries and matching Debian copyright notices under `/system` and `/licenses`; no HTTP client daemon is included.

### SQL example

```sql
SELECT status, content FROM http_get('https://example.org/');
```


## Licenses and updates

The extension is licensed under `MIT`. Its copyright notice and notices for bundled runtime packages are included under `/licenses/<package>/`. The image includes no source archives. Renovate tracks the suite-specific PGDG package; rebuild against the supported Debian suite to refresh the package and linked runtime files, then review dependency and notice changes.
