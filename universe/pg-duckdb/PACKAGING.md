# pg_duckdb packaging notes

CNPG Extensions builds pg_duckdb from source while Debian/PGDG packaging,
maintenance and dependency-backport decisions remain unresolved. Adoption needs
an installable PGDG package set for both Bookworm and Trixie. See the
[Debian inclusion appendix](#appendix-debian-and-pgdg-inclusion) for ownership,
unresolved decisions and technical steps.

The current source build follows upstream's default release settings, with
Clang for DuckDB and GCC for pg_duckdb; Trixie supplies Clang. The final CNPG
extension image contains the extension payload rather than a complete PostgreSQL
server.

## SBOM contents

The shared generator records shipped files and actual Debian package ownership.
The recipe hook uses the package boundaries of Debian DuckDB 2.0.0+dfsg2-1,
so the source-built image and a future Debian-package image expose comparable
library identities. This is a package-level inventory, not a separate record
for every embedded source component.

- Keep pg_duckdb and DuckDB as source-built packages.
- Keep separate source-built records for the seven libraries Debian DuckDB uses
  as system packages: yyjson (`libyyjson0`), LZ4 (`liblz4-1`), Zstandard
  (`libzstd1`), Brotli (`libbrotli1`), Mbed TLS crypto (`libmbedcrypto16`),
  Snappy (`libsnappy1v5`) and xxHash (`libxxhash0`). This is a fixed inventory
  reviewed against the supported source revision and default build. xxHash is
  nested inside the vendored Zstandard tree but remains a separate record.
- Preserve their real upstream/source identities. A source-built Brotli is not
  a Debian-installed `libbrotli1`; the Debian name is explanatory `sourceInfo`,
  never a fabricated `pkg:deb` identifier. A system LZ4 and a vendored LZ4 may
  coexist and must not be deduplicated merely because they implement the same
  library.
- Fold code Debian leaves internal, such as RE2, jemalloc, fmt, miniz and Parquet
  format code, into DuckDB's package record. Fold vendored PostgreSQL/PgBouncer
  code into pg_duckdb. Generated Unicode, CLDR and time-zone data are covered by
  DuckDB rather than separate data-package records.

The boundary follows what Debian's DuckDB build actually separates, not every
library available somewhere in the Debian archive. For example, Debian packages
RE2 and jemalloc independently, but the inspected DuckDB package still embeds
its modified copies. Reassess this recipe mapping when Debian changes that
choice. Do not infer new entries from the builder's installed development tools.

### Copyright files and release review

Like Debian's [copyright packaging](https://www.debian.org/doc/debian-policy/ch-docs.html#copyright-information),
this recipe assembles consolidated copyright files from reviewed source
locations. [The extraction script](licenses.sh) reads standalone license files
directly and uses explicit `sed` ranges for embedded notices. It downloads Debian
DuckDB 2.0.0+dfsg2-1's source-package copyright document as the baseline and
includes supplemental original notices from the reviewed source snapshot.
The other copyright files cover pg_duckdb and the
seven library counterparts that Debian packages separately. They preserve the
actual bundled versions' terms, rather than substituting copyright files from
possibly different installed Debian versions.

The build writes nine files to `/licenses/<name>/copyright`; the Dockerfile
copies that directory into the final image. License text is not duplicated in
this repository.
Common-license texts referenced by the source documents are included so the
extension's attribution does not depend on `/usr/share/common-licenses` existing
in another image. Source paths and supplemental notice URLs remain in the files.
The SBOM associates them with their containing packages; composite terms use
`LicenseRef` and extracted licensing information. Internal components remain
covered by DuckDB, not extra package records.

`evidence.py` has one static library table containing upstream versions,
identities, Debian counterparts and vendor paths. There is no Ninja dependency
traversal, header-version parser or general-purpose comment parser. Notice
locations, marker ranges and line ranges are explicitly reviewed for the pinned
sources. Missing supplemental documents are fetched from explicit upstream URLs.
Both source revision checks ensure changed sources receive a release review.
When updating the sources or build settings, review the dependency inventory,
Debian's packaging boundary and all copyright files together. Unknown snapshot
versions, such as this Snappy copy, remain omitted rather than guessed.

The SPDX document states its scope explicitly. Absence of an internal component
record is not evidence that its code is absent or unaffected by an advisory.

The shared system-library helper stages additional runtime libraries under
`/system`, excluding libraries supplied by the PostgreSQL base image, and preserves
their notices. Consequently, a Debian library used from the base image belongs
in the base image's inventory; installing its development package in the builder
does not create a shipped dependency record in the extension image.
Upstream's default build does not ship its loadable httpfs here;
its curl/OpenSSL build dependencies must not be counted merely because apt
installed them.

### Measured native amd64 payload

A local build of pg_duckdb 1.2.0 on the PostgreSQL 18 minimal Trixie base
confirmed the following boundary (2026-11-15):

| Category | Count | Treatment |
|---|---:|---|
| Debian shared-library packages supplying resolved runtime dependencies | 5 | `libc6`, `libgcc-s1`, `libstdc++6`, `liblz4-1`, `libxxhash0`; all supplied by the base image |
| Additional Debian-owned shared-library packages shipped in this extension payload | 0 | No additional `pkg:deb` records should be invented |
| Source-built DuckDB engine | 1 | `libduckdb.so` in `/system`, with its upstream source identity |
| Source-built library counterparts Debian packages separately | 7 | Brotli, LZ4, Mbed TLS, Snappy, yyjson, Zstandard and xxHash, embedded in DuckDB |

Together with pg_duckdb, this produces nine source-package records. LZ4 and
xxHash occur both as base-image shared libraries and as DuckDB's embedded
copies; reporting one does not account for the other.

The original native build passed PostgreSQL 18 preload, `CREATE EXTENSION` and
a forced `DuckDBScan` query. Follow-up notice validation reuses that compiled
builder with the current evidence recorder and the Dockerfile's individual
COPY operations. All 41 shared tests passed. The generated SPDX has nine source
packages and nine consolidated copyright files. Artifact checks verified that
the contents of all 406 previously collected notice files remain present, with
containing-package relationships and extracted license text.
This does not claim a new compilation or native ARM64 coverage.

These are measured counts for this version, platform and base, not assertions
that future recipes must keep a fixed inventory. The native build needed
`libicu-dev` for PostgreSQL locale headers; a build dependency alone is not
evidence that its library is shipped. Bookworm and native ARM64 builds and
hosted signing/SLSA acceptance are not covered by this local measurement.

`evidence.py` records package identities and the actual files copied by the
Dockerfile. The final image copies the installed extension into `/lib` and
`/share`, plus `/system` and `/licenses`; there is no intermediate `/payload`.
The extraction commands cover the nested and later-source notices found
in the audit, including ALP/ALPRD, Salesforce, Martin Ankerl, ADBC/nanoarrow,
Preshing's semaphore, miniz, Brotli and public-domain statements.

`augment_spdx.py` preserves the generator's existing records and adds source
packages through its hook interface. Builder reports are private validation
inputs; consumers use the standard SPDX document described in the
[shared dependency guidance](../../source-build/README.md#dependency-evidence-in-the-sbom).
Neither helper is a generic Universe dependency or license framework. Build-input
relationships do not prove that every object survives linker dead-code elimination.

Review component boundaries, identities, notice sources and applicable obligations
when updating the release. Missing or unresolved license information does not
itself establish compliance with the
[Open Source Licensing Policy](../../README.md#open-source-licensing-policy).

## Source acquisition

The Dockerfile clones the release named by `EXT_VERSION` and initializes its Git
submodules recursively, following upstream's checkout instructions. The upstream
CMake configuration fetches the matching pinned httpfs revision. The evidence
step reads the actual pg_duckdb and DuckDB checkout revisions after the build.
Loadable httpfs is not installed in the image, matching upstream; downloaded
extensions are outside the image SBOM. No GitHub API lookup or archive-specific build patch is needed.

BuildKit can reuse a cached checkout for an unchanged recipe and version; invalidate
that cache when a fresh checkout is needed. Release tags are not frozen across
separate architecture builds.

## Appendix: Debian and PGDG inclusion

A separate native amd64 investigation demonstrated that pg_duckdb 1.2.0 builds
and runs against Debian unstable's shared DuckDB 2.0 with build-system changes
and the missing development headers supplied, without pg_duckdb C++ changes.
DuckDB itself also built and passed all nine existing Debian smoke tests in a
clean Bookworm runtime environment. The combined Bookworm pg_duckdb stack,
Trixie builds and native ARM64 validation remain outstanding. These experiments
do not validate this recipe's current build or hosted release pipeline.

Using a system DuckDB library is therefore technically feasible; a required
DuckDB fork or wholesale unbundling is not an established blocker for that
version pair. Upstream's [system-library discussion](https://github.com/duckdb/pg_duckdb/issues/554)
describes the remaining version coupling. Existing Debian packaging does not,
however, settle publication and maintenance for both target suites.

### 1. DuckDB Debian maintainers

- **Unresolved decisions:** acceptance of development-package fixes; supported
  ABI compatibility; maintenance expectations for remaining bundled components.
- **Technical work:** complete `libduckdb-dev` with the required namespaced fmt
  and RE2 headers; review patches and test pg_duckdb compatibility.

### 2. pg_duckdb packaging contributor and Debian PostgreSQL reviewers

- **Unresolved decisions:** ongoing package ownership, sponsorship, and Debian
  archive acceptance.
- **Technical work:** create PGXS/`pg_buildext` packaging; use system DuckDB;
  declare version constraints; configure packaged extensions; complete copyright
  review and offline tests.

### 3. Backport contributors and archive maintainers

- **Unresolved decisions:** which dependencies need backporting on each suite;
  whether they are published through Debian Backports, PGDG, or a combination;
  maintenance ownership and PGDG acceptance of the resulting package set.
- **Technical work:** prepare Bookworm's demonstrated yyjson and Mbed TLS
  backports and DuckDB compatibility patches, using PGDG's libpq18; validate
  Trixie independently; test the complete stack on amd64 and arm64; publish
  pg_duckdb in PGDG for both suites and the required PostgreSQL versions.

Dependency publication need not all happen in PGDG. The requirement is an
installable package set from the agreed repositories. PGDG's
[packaging policy](https://wiki.postgresql.org/wiki/Apt/Packages) favors alignment
with Debian unstable; successful local builds do not replace archive acceptance
and publication.

### 4. CNPG Extensions maintainers

- **Technical work:** once published in PGDG, configure the required repositories,
  integrate through the existing Debian build infrastructure, and run runtime,
  SBOM, security and release checks.
