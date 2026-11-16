# asn1oid
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

ASN.1 object identifier values as a native PostgreSQL type. See the [upstream project](https://github.com/df7cb/pgsql-asn1oid) for its API and release history.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the asn1oid extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-asn1oid
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: asn1oid
```

### 2. Enable the extension in a database

Install the SQL extension in a database with a CNPG `Database` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-asn1oid-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-asn1oid
  extensions:
  - ensure: present
    name: asn1oid
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

A SQL check that exercises the installed extension is:

```sql
SELECT '2.16.840.1.101.3.4.2.1'::asn1oid::text = '2.16.840.1.101.3.4.2.1';
```

## Package, dependencies and maintenance

The image installs PGDG package `postgresql-18-asn1oid` at the Debian version recorded in `metadata.hcl`. Package updates are tracked by Renovate; review changes against the package's control file and rerun the target's build. The package is available for PostgreSQL 18 on both Bookworm and Trixie, amd64 and arm64. It depends on the CNPG PostgreSQL 18 base image and libc; no additional runtime package is installed. The asn1oid module uses GPL-3.0-or-later licensing. Its Debian copyright file is included under `/licenses/`.

