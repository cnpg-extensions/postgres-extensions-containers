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
  Snappy (`libsnappy1v5`) and xxHash (`libxxhash0`). Selection still follows the
  shipped library's actual build inputs. xxHash is nested inside the vendored
  Zstandard tree and is recorded separately when used.
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

Original notices remain under `/licenses`, including notices of folded
components. The containing package aggregates their full license text using
SPDX `LicenseRef` and extracted licensing information, preserves copyright
attribution, and associates every notice through `DISTRIBUTION_ARTIFACT`.
Build evidence records only the public package identities. Internal code's
notices are collected directly into the containing package, preserving source
paths without constructing a second component/version graph. The SPDX document comment states this scope explicitly. Consumers
must not interpret absence of an internal component record as proof that its
code is absent or unaffected by an advisory.

Versions come from selected source headers and release metadata where available.
Modified snapshots retain source URLs identifying their revision and vendor path.
Unknown release versions are omitted from SPDX `versionInfo`; commit/path strings
are not synthesized as versions. DuckDB's reported version override is recorded
separately from its source identity. The attached SBOM contains these identities;
this document does not duplicate their pins.

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
builder with the current evidence collector and the Dockerfile's individual
COPY operations. All 42 shared tests passed. The generated SPDX has nine source
packages and 406 notice files: checks verified preservation of every previously
collected notice, the missing attribution identified by the copyright audit,
and each file's containing-package relationship and extracted license text.
This does not claim a new compilation or native ARM64 coverage.

These are measured counts for this version, platform and base, not assertions
that future recipes must keep a fixed inventory. The native build needed
`libicu-dev` for PostgreSQL locale headers; a build dependency alone is not
evidence that its library is shipped. Bookworm and native ARM64 builds and
hosted signing/SLSA acceptance are not covered by this local measurement.

`evidence.py` collects original notices and records the files copied by the
Dockerfile. The final image copies the installed extension into `/lib` and
`/share`, plus the shared helper's `/system` and `/licenses` directories;
there is no intermediate `/payload` directory.

Notice collection covers selected DuckDB `src/` and extension inputs, adjacent
nested LICENSE files, and selected third-party directories. It preserves legal
comment blocks throughout source files, including notices after banners/includes
and later notices in amalgamated sources. This covers ALP/ALPRD, Salesforce's
merge-sort code, Martin Ankerl's hashing, ADBC/nanoarrow, Preshing's semaphore,
and additional miniz/Brotli notices. Public-domain statements are retained too.
Referenced upstream license/NOTICE files absent from the vendored tree are
included with their source URLs. Those notice revisions identify attribution
sources, not inferred versions of embedded code. Generated-data notices remain
part of DuckDB's combined terms.

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
