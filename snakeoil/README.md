# pg_snakeoil
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

[pg_snakeoil](https://github.com/credativ/pg_snakeoil) is a PostgreSQL extension that uses the ClamAV antivirus engine to scan data stored in PostgreSQL for malware. It provides SQL functions to scan bytea values against ClamAV virus signature databases.

## Usage

### 1. Add the snakeoil extension image to your Cluster

Define the `snakeoil` extension under the `postgresql.extensions` section of
your `Cluster` resource. The extension requires setting
`pg_snakeoil.signature_dir` to point to the bundled ClamAV signatures:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-snakeoil
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    parameters:
      pg_snakeoil.signature_dir: "/extensions/snakeoil/share/clamav"

    extensions:
    - name: snakeoil
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-snakeoil
        reference: ghcr.io/cnpg-extensions/snakeoil:1.4-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_snakeoil` in a specific database by creating or updating a
`Database` resource, or by running `CREATE EXTENSION` directly in `psql`. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-snakeoil-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-snakeoil
  extensions:
  - name: snakeoil
    # renovate: suite=trixie-pgdg depName=postgresql-18-snakeoil extractVersion=^(?<version>\d+)
    version: '1'
```
Alternatively, you can enable the extension directly with SQL:

```sql
CREATE EXTENSION pg_snakeoil;
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_snakeoil` listed among the installed extensions.

## Production ClamAV Signatures

> [!WARNING]
> **No approach for providing production ClamAV signatures has been decided
> yet. This must be solved before `pg_snakeoil` is useful for real antivirus
> scanning.** The bundled stub database (see below) only contains the EICAR
> test signature and will not detect real malware.

ClamAV releases signature database updates daily. Two approaches are viable
for providing current signatures to `pg_snakeoil` in a CNPG cluster:

### Option A: Sidecar container running freshclam

Run a sidecar container alongside PostgreSQL that executes `freshclam
--daemon`, writing updated signatures to a shared `emptyDir` volume. Set
`pg_snakeoil.signature_dir` to the volume mount path. This is the
production-grade approach since signatures stay current without any
cluster restarts.

```yaml
spec:
  # Mount a shared volume for ClamAV signatures
  # (requires CNPG support for extra volumes on the PostgreSQL pod)
  postgresql:
    parameters:
      pg_snakeoil.signature_dir: "/clamav-data"
```

### Option B: Bake signatures into the image at build time

Run `freshclam` during the Docker image build and `COPY` the resulting
`.cvd`/`.cld` files into the image. The image then ships with a snapshot of
the signatures current at build time. This approach is simple to deploy but
signatures go stale quickly — ClamAV's `freshclam` will refuse to scan if
the database is more than a few days old.

---

## Known Caveats

- **Stub ClamAV database — not suitable for production**: The extension
  requires ClamAV signature databases to be present at `CREATE EXTENSION`
  time. This image bundles a minimal stub `.hdb` file containing only the
  EICAR test signature, sufficient for the extension to initialize. It will
  not detect real malware. See the section above for approaches to providing
  real signatures.
- **`pg_snakeoil.signature_dir` must be configured**: Without setting this GUC,
  `CREATE EXTENSION pg_snakeoil` will fail with a "Can't get file status" error
  because libclamav cannot find signature files. The operator automatically sets
  this parameter to `/extensions/snakeoil/share/clamav` via the metadata, but
  you can also set it explicitly in `postgresql.parameters`.
- **Runtime library dependency**: `libclamav12` is bundled in the image under
  `/system/`.
- **License**: `pg_snakeoil` itself is PostgreSQL-licensed, but its runtime
  dependency `libclamav12` is LGPL-2+, which is why this extension is hosted in
  the CNPG Extensions project rather than upstream.

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `snakeoil` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
