# ICU functions

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

icu_ext exposes ICU internationalization functions for text transformation, comparison, collation, and Unicode metadata. See the [upstream project](https://github.com/dverite/icu_ext) for the extension documentation.

This image supports PostgreSQL 18 on Debian Bookworm and Trixie. The selected PGDG package versions are maintained independently per suite in `metadata.hcl`.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then use the CronJob to install and refresh the catalog. These
examples inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the icu-ext extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-icu-ext
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: icu-ext
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION icu_ext;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

The PGDG package links to ICU 76 on Trixie and ICU 72 on Bookworm. The supported CNPG base images provide these runtime libraries and their notices; ICU locale data is supplied by the ICU runtime package.

### SQL example

```sql
SELECT icu_transform('Hello, PostgreSQL', 'Any-Upper');
```


## Licenses and updates

The extension is distributed under its custom permissive Verite license (`LicenseRef-verite`). Its PGDG copyright notice is included under `/licenses/<package>/`. The supported CNPG base images already provide the linked ICU runtime libraries, so this extension adds no ICU files under `/system`. The image includes no source archives. Renovate tracks the suite-specific PGDG package; rebuild against the supported Debian suite and review package and notice changes.
