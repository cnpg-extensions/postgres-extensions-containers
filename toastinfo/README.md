# toastinfo
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[toastinfo](https://github.com/df7cb/toastinfo) describes how PostgreSQL
stores variable-length values, including inline, compressed, and out-of-line
TOAST values. It does not need to be preloaded.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the toastinfo extension image to your Cluster

Add the image to a Cluster:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-toastinfo
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: toastinfo
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION toastinfo;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Use pg_toastinfo and pg_toastpointer to inspect a value:

~~~sql
CREATE EXTENSION toastinfo;
SELECT pg_toastinfo(value), pg_toastpointer(value) FROM my_table;
~~~

## Licenses and Copyright

The package copyright and license notice are included in the image under
/licenses/postgresql-18-toastinfo/.
