# pg-gvm

pg-gvm adds Greenbone helper functions to PostgreSQL, including host-list matching, regular-expression matching and iCalendar schedule calculations. It supplies the SQL library only; it does not install or operate Greenbone Vulnerability Manager services.

The PGDG PG18 package is available on Trixie for amd64 and arm64. Bookworm has no PG18 package.

[Upstream project](https://github.com/greenbone/pg-gvm).

## Install and use

~~~yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-gvm
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    extensions:
    - name: pg-gvm
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pg-gvm
        reference: ghcr.io/cnpg-extensions/pg-gvm:22.6.18-18-trixie
      ld_library_path: [system]
---
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-gvm-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-gvm
  extensions:
  - name: pg-gvm
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg-gvm extractVersion=^(?<version>\d+\.\d+)
    version: '22.6'
~~~

The image installs the pg-gvm SQL extension but not a GVM manager or scanner. A standalone expression check is:

~~~sql
SELECT regexp('host.example', '^host');
~~~

The package also includes host-list and iCalendar helpers used by Greenbone SQL workflows. `hosts_contains()` reads Greenbone's `meta` table, so it is exercised only in a database with that application schema installed.

## Package, licensing and updates

PGDG package: 22.6.17-1.pgdg13+2; SQL version: 22.6. The extension is GPL-3.0-or-later and includes AGPL-3.0-or-later files. Copyright notices for the extension and bundled runtime packages are under `/licenses/<package>/`. The image includes no source archives.

Renovate tracks the PGDG package. Rebuild after package or base-image security updates and review the runtime libraries and notices.

The regex and calendar helpers work without a Greenbone application schema.
These helpers do not create files; the image adds no listener or background
service.

The runtime closure is dynamically linked. ICU and PCRE2 are redistributed under
their permissive notices; the GCC runtime libraries use the GCC Runtime Library
Exception. Copyright notices for bundled runtime packages are under
`/licenses/<package>/`. The matching CNPG base supplies glibc and the ELF loader.
