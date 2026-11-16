# preprepare

pre prepare your PostgreSQL statements server side. [Upstream documentation](https://apt.postgresql.org/pub/repos/apt/).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Usage

### 1. Add the preprepare extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-preprepare
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: preprepare
```

### 2. Enable the extension in a database

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-preprepare-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-preprepare
  extensions:
  - name: pre_prepare
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

## Operation and privileges

This image provides SQL extension `pre_prepare`. Prepared statements and their source table are session-local; no files are needed. Use `prepare_all('schema.table')` to load statement definitions from an administrator-controlled table of complete PREPARE statements. Restrict which users can modify the source table.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

PostgreSQL. Redistribution notices are preserved under `/licenses/`.

The PGDG copyright labels its notice(s) `BSD`. The permission and
disclaimer text matches the [SPDX PostgreSQL license template](https://github.com/spdx/license-list-data/blob/main/json/details/PostgreSQL.json),
which allows copyright-holder substitutions in the disclaimer paragraphs.
The metadata uses that SPDX identifier; the image retains the complete original
package copyright, including every named holder and notice.
