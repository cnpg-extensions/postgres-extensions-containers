# plsh

PL/sh procedural language for PostgreSQL 18. [Upstream documentation](https://github.com/petere/plsh).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Usage

### 1. Add the plsh extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-plsh
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: plsh
```

### 2. Enable the extension in a database

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-plsh-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-plsh
  extensions:
  - name: plsh
```

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

## Operation and privileges

PL/sh is an untrusted language: only superusers can create its functions. Commands run as the PostgreSQL OS user and inherit its filesystem and network access. This image supports the `/bin/sh` already supplied by the matching CNPG minimal image, with shell built-ins only. It does not add arbitrary external commands or support file-producing functions. Restrict function EXECUTE grants to trusted administrators.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

PostgreSQL. Redistribution notices are preserved under `/licenses/`.
Maintained by Jeremy Schneider (@ardentperf).
