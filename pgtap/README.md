# pgTAP

Unit testing framework extension for PostgreSQL 18. [Upstream documentation](https://pgtap.org/).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Usage

### 1. Add the pgtap extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgtap
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: pgtap
```

### 2. Enable the extension in a database

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgtap-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgtap
  extensions:
  - name: pgtap
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

## Operation and privileges

The server-side TAP assertion functions return text through SQL. Test runners remain separate clients connected to the CNPG-managed endpoint; they own report files and retention.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

PostgreSQL. Redistribution notices are preserved under `/licenses/`.
