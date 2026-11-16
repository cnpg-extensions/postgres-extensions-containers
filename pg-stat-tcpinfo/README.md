# pg_stat_tcpinfo

Live Linux TCP socket statistics exposed through SQL. [Upstream documentation](https://github.com/jakubwartakEDB/pg_stat_tcpinfo).

## Supported images

PostgreSQL 18 on Debian Bookworm and Trixie, for amd64 and arm64.

## Declarative setup

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-stat-tcpinfo
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
    extensions:
    - name: pg-stat-tcpinfo
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-tcpinfo
        reference: ghcr.io/cnpg-extensions/pg-stat-tcpinfo:1.1-18-trixie
---
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-stat-tcpinfo-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-stat-tcpinfo
  extensions:
  - name: pg_stat_tcpinfo
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-tcpinfo extractVersion=^(?<version>\d+\.\d+)-
    version: '1.1'
```

For Bookworm, use the `postgresql-minimal-bookworm` catalog and the corresponding
`-18-bookworm` extension image tags. No shared preload configuration is needed.

## Query TCP statistics

As an administrator, grant monitoring access to the application role:

```sql
GRANT pg_monitor TO app;
```

Connect over TCP as that role, then query:

```sql
SELECT pid, src_addr, src_port, dst_addr, dst_port, state,
       tcpinfo->>'rtt' AS rtt
FROM pg_stat_tcpinfo
WHERE state = 'ESTABLISHED'
ORDER BY pid;
```

The extension reports sockets owned by PostgreSQL's OS user within the pod's
network namespace. It requires Linux procfs and netlink socket diagnostics;
restricted sandbox policies can prevent collection. No extra Linux capabilities
are required in the tested stock CNPG environment. UNIX-domain connections do
not appear as TCP sockets; use a TCP connection when verifying the view.

Access is restricted to `pg_read_all_stats` (also inherited by `pg_monitor`),
not PUBLIC. These monitoring roles expose additional database statistics;
grant them only to appropriate users. No persistent files or maintenance daemon
are needed.

## Licensing and payload

The extension and Debian packaging use the **PostgreSQL** license. The full
copyright and license notice is shipped at
`/licenses/postgresql-18-pg-stat-tcpinfo/copyright`.

The image contains the extension library, its LLVM bitcode, SQL/control files,
and notice. It bundles no system libraries: libc and the ELF loader come from
the matching PostgreSQL base image. The payload belongs in the top-level
README's CNCF-compatible declared-license group; this classification describes
licenses, not a claim of upstream CNCF project acceptance.

## Updates and validation

Renovate tracks both Debian package pins and the documented image tags. SQL
versions are extracted from the verified package version shape; review the
packaged control files and upgrade scripts when that shape changes. Rebuild
and validate both distributions and architectures after package updates.

The extension-specific Chainsaw test exercises real behavior through the mounted
image, in addition to the shared installation checks. Run:

```sh
task checks TARGET=pg-stat-tcpinfo
task e2e:test:full TARGET=pg-stat-tcpinfo
```

Maintained by the repository maintainers.
