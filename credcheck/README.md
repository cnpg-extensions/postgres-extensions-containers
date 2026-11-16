# credcheck

PostgreSQL username/password checks. [Upstream documentation](https://github.com/MigOpsRepos/credcheck).

Follow the [quick start](../README.md#quick-start) to install the catalog and set up
extension-update email alerts before enabling weekly maintenance. These examples
inherit image references and runtime settings from the catalog.

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## PostgreSQL compatibility

credcheck 6.0 images using PGDG package revision `+2` require PostgreSQL 18.7
or later within major version 18. Upgrade PostgreSQL first: on 18.6, credcheck
prevents startup with `undefined symbol: heap_datum_check`. CNPG does not
enforce extension minimum minor versions.

## Declarative setup

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-credcheck
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
    parameters:
      credcheck.encrypted_password_allowed: 'on'
    shared_preload_libraries:
    - credcheck
    extensions:
    - name: credcheck
```

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-credcheck-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-credcheck
  extensions:
  - name: credcheck
```

## Operation and privileges

CNPG reconciles role credentials using precomputed SCRAM verifiers. Set `credcheck.encrypted_password_allowed: "on"` so those updates succeed. Plaintext password policy cannot inspect precomputed verifiers; enforce equivalent policy where Kubernetes password Secrets are generated. SQL role changes using plaintext passwords remain checked.

Credential checks apply to role creation and password changes. Configure policy settings in `postgresql.parameters`; only administrators should change them.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Project automation tracks package updates and rebuilds the extension images.
Use the catalog maintenance schedule in the quick start to consume published
PostgreSQL and extension image updates. Monitor pending SQL extension upgrades
and review them separately; SQL versions need not match package versions.

## Licenses and ownership

MIT. Redistribution notices are preserved under `/licenses/`.
Maintained by Jeremy Schneider (@ardentperf).
