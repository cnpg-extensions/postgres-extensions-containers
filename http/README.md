# HTTP requests from PostgreSQL

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

http adds HTTP client functions to PostgreSQL so SQL can call HTTP services through libcurl. See the [upstream project](https://github.com/pramsey/pgsql-http) for the extension documentation.

This image supports PostgreSQL 18 on Debian Bookworm and Trixie. The selected PGDG package versions are maintained independently per suite in `metadata.hcl`.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the http extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-http
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: http
```

### 2. Enable the extension in a database

```yaml
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

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

The PGDG package links to libcurl. The build stages the resolved non-core shared libraries and matching Debian copyright notices under `/system` and `/licenses`; no HTTP client daemon is included.

### SQL example

```sql
SELECT status, content FROM http_get('https://example.org/');
```


## Licenses and updates

The extension is licensed under `MIT`. Its copyright notice and notices for bundled runtime packages are included under `/licenses/<package>/`. The image includes no source archives. Renovate tracks the suite-specific PGDG package; rebuild against the supported Debian suite to refresh the package and linked runtime files, then review dependency and notice changes.
