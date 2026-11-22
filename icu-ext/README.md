# ICU functions

<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Exposes ICU internationalization functions for text transformation,
comparison, collation, and Unicode metadata. Use it to sort text according
to different languages’ rules, such as putting names in alphabetical order.

For more information, see the [upstream documentation](https://github.com/dverite/icu_ext).

### 1. Add the icu-ext extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

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

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

The ICU version and language rules depend on the Debian release used by your
image, such as Bookworm or Trixie.

```sql
SELECT icu_transform('Hello, PostgreSQL', 'Any-Upper');
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
