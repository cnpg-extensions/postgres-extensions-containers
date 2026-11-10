# PostgreSQL Anonymizer
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[PostgreSQL Anonymizer](https://gitlab.com/dalibo/postgresql_anonymizer)
provides anonymization and data masking through the `anon` SQL extension.
This image builds upstream release **3.3.2** for PostgreSQL 18 on Debian
Bookworm and Trixie, including the upstream fake-data CSV datasets.

## Usage

Add the extension image to your CloudNativePG Cluster and preload `anon`:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-anonymizer
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    shared_preload_libraries:
    - anon
    extensions:
    - name: postgresql-anonymizer
      image:
        reference: ghcr.io/cnpg-extensions/postgresql-anonymizer:3.3.2-18-trixie
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

For declarative installation, use the **SQL name** `anon` in a Database resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-anonymizer-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-anonymizer
  extensions:
  - name: anon
    version: '3.3.2'
```

Dataset initialization remains a separate superuser step. For masking rules,
permissions, and transparent dynamic masking, follow the
[upstream documentation](https://postgresql-anonymizer.readthedocs.io/).

## Contributors

Maintained by Jeremy Schneider (@ardentperf).

## Licenses and Copyright

The extension uses the PostgreSQL license. The image bundles its license and
Rust dependency notices under `/licenses/rust/`. The source archive and upstream
Cargo.lock are pinned by the shared PGRX build workflow.
