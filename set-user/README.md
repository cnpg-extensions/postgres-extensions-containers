# set_user

PostgreSQL privilege escalation with enhanced logging and control. [Upstream documentation](https://github.com/pgaudit/set_user).

## Supported images

PostgreSQL 18; Debian Trixie and Bookworm; amd64 and arm64 build targets.

## Declarative setup

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-set-user
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    shared_preload_libraries: ["set_user"]
    extensions:
    - name: set-user
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-set-user
        reference: ghcr.io/cnpg-extensions/set-user:4.3.0-18-trixie
```

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-set-user-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-set-user
  extensions:
  - name: set_user
    # renovate: suite=trixie-pgdg depName=postgresql-18-set-user extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+[.][0-9]+)
    version: '4.3.0'
```

## Operation and privileges

Role switching is audited through normal PostgreSQL logging. Restrict EXECUTE on elevation functions and configure allowed roles. Logs follow the CNPG logging pipeline; retain and rotate them in the cluster logging backend. This image does not create separate log files.

## Dependencies and updates

The image contains only the PGDG package server payload and license notices.
The matching CNPG minimal image supplies PostgreSQL, libc and its base runtime.
Renovate tracks the pinned extension package. For an extension or base-runtime
security fix, update the affected package/base image, rebuild every advertised
architecture. SQL versions must be checked against
the installed control file separately because they need not match package versions.

## Licenses and ownership

PostgreSQL. Redistribution notices are preserved under `/licenses/`.
Maintained by Jeremy Schneider (@ardentperf).

The PGDG copyright labels its notice(s) `PostgreSQL and Crunchy`. The permission and
disclaimer text matches the [SPDX PostgreSQL license template](https://github.com/spdx/license-list-data/blob/main/json/details/PostgreSQL.json),
which allows copyright-holder substitutions in the disclaimer paragraphs.
The metadata uses that SPDX identifier; the image retains the complete original
package copyright, including every named holder and notice.
