# pgextwlist

[pgextwlist](https://github.com/dimitri/pgextwlist) lets administrators allow non-superusers to install an approved
selection of PostgreSQL extensions.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/dimitri/pgextwlist).

### 1. Add the pgextwlist extension image to your Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgextwlist
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - pgextwlist
    parameters:
      extwlist.extensions: dblink
    extensions:
    - name: pgextwlist
```

### 2. Verify installation

Connect with `psql` and run `SHOW extwlist.extensions;` to check the configured
allowlist.

## Operation and privileges

This module has no CREATE EXTENSION artifact. Its preload hook allows non-superusers to install administrator-allowlisted extensions that normally require superuser privileges; PostgreSQL trusted extensions retain their ordinary permissions. The example allowlists `dblink`, already present in the minimal PostgreSQL image. Optional custom script execution is not configured or supported by this image.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
