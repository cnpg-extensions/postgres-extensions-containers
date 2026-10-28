# credcheck

PostgreSQL username/password checks. [Upstream documentation](https://github.com/MigOpsRepos/credcheck).

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Declarative setup

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-credcheck
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    parameters:
      credcheck.encrypted_password_allowed: "on"
    shared_preload_libraries: ["credcheck"]
    extensions:
    - name: credcheck
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-credcheck
        reference: ghcr.io/cnpg-extensions/credcheck:6.0-18-trixie
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
    version: "5.0.0"
```

## Operation and privileges

CNPG reconciles role credentials using precomputed SCRAM verifiers. Set `credcheck.encrypted_password_allowed: "on"` so those updates succeed. Plaintext password policy cannot inspect precomputed verifiers; enforce equivalent policy where Kubernetes password Secrets are generated. SQL role changes using plaintext passwords remain checked.

Credential checks apply to role creation and password changes. Configure policy settings in `postgresql.parameters`; only administrators should change them.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Renovate tracks the pinned extension package. For an extension or base-runtime
security fix, update the affected package/base image, rebuild every advertised
architecture. SQL versions must be checked against
the installed control file separately because they need not match package versions.

## Licenses and ownership

MIT. Redistribution notices are preserved under `/licenses/`.
Maintained by Jeremy Schneider (@ardentperf).
