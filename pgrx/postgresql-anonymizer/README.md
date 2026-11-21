# PostgreSQL Anonymizer
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

Lets you anonymize data and define masking rules through
the `anon` SQL extension. It includes fake-data datasets for generating
replacement values.

Follow the [quick start](../../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://gitlab.com/dalibo/postgresql_anonymizer).

### 1. Add the postgresql-anonymizer extension image to your Cluster

Add the extension image to your CloudNativePG Cluster and preload `anon`:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-anonymizer
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - anon
    extensions:
    - name: postgresql-anonymizer
```

Connect as a superuser to the target database and enable the extension:

```sql
CREATE EXTENSION anon;
SELECT anon.init('/extensions/postgresql-anonymizer/share/extension/anon');
SELECT anon.fake_first_name();
```

Use the explicit mounted data path: upstream's argument-free `anon.init()`
looks in PostgreSQL's built-in share directory, while CloudNativePG mounts
extension images separately. Keep the Cluster extension name
`postgresql-anonymizer` to use the path above; adjust it if you rename the mount.
Initialization loads the datasets needed by the legacy `fake_*` functions.
Upstream `dummy_*` functions generate data without this initialization.

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION anon;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx anon
```

You should see `anon` listed with its installed SQL version.

Dataset initialization remains a separate superuser step. For masking rules,
permissions, and transparent dynamic masking, follow the
[upstream documentation](https://postgresql-anonymizer.readthedocs.io/).

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
