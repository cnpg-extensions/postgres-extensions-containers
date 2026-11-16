# Perl-compatible regular expressions

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

pgpcre adds a PCRE2-backed regular-expression type and capture functions to PostgreSQL. See the [upstream project](https://github.com/petere/pgpcre) for the extension documentation.

This image supports PostgreSQL 18 on Debian Bookworm and Trixie. The selected PGDG package versions are maintained independently per suite in `metadata.hcl`.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the pgpcre extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgpcre
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pgpcre
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION pgpcre;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

The PGDG package links to PCRE2 10.42 on Bookworm and 10.46 on Trixie. The supported CNPG base images provide these runtime libraries, so the extension adds no files under `/system`.

### SQL example

```sql
SELECT pcre_match('^([A-Z]+)-([0-9]+)$'::pcre, 'DB-42');
```


## Licenses and updates

The extension is licensed under `PostgreSQL`. Its copyright notice is included under `/licenses/<package>/`. The supported CNPG base images provide the runtime libraries required by the extension, so no files are staged under `/system`. The image includes no source archives. Renovate tracks the suite-specific PGDG package; rebuild against the supported Debian suite and review package and notice changes.
