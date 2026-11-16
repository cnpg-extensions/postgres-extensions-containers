# ICU functions

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

icu_ext exposes ICU internationalization functions for text transformation, comparison, collation, and Unicode metadata. See the [upstream project](https://github.com/dverite/icu_ext) for the extension documentation.

This image supports PostgreSQL 18 on Debian Bookworm and Trixie. The selected PGDG package versions are maintained independently per suite in `metadata.hcl`.

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Install with CloudNativePG

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-icu-ext
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
    - name: icu-ext
---
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-icu-ext-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-icu-ext
  extensions:
  - name: icu_ext
```

The PGDG package links to ICU 76 on Trixie and ICU 72 on Bookworm. The supported CNPG base images provide these runtime libraries and their notices; ICU locale data is supplied by the ICU runtime package.

### SQL example

```sql
SELECT icu_transform('Hello, PostgreSQL', 'Any-Upper');
```


## Licenses and updates

The extension is distributed under its custom permissive Verite license (`LicenseRef-verite`). Its PGDG copyright notice is included under `/licenses/<package>/`. The supported CNPG base images already provide the linked ICU runtime libraries, so this extension adds no ICU files under `/system`. The image includes no source archives. Renovate tracks the suite-specific PGDG package; rebuild against the supported Debian suite and review package and notice changes.
