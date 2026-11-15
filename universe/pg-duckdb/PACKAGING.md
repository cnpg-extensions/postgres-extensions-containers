# pg_duckdb packaging notes

## Path to Debian and PGDG packages

The goal is pg_duckdb available through PGDG for Bookworm and Trixie, with an
installable dependency chain, before adopting those packages in CNPG Extensions.
The remaining packaging, maintenance and archive decisions justify keeping the
CNPG Extensions source-build recipe while that work is unresolved. Revisit the
recipe when the required packages are published and pass the shared integration
checks.

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

The current source build follows upstream's default release settings, with
Clang for DuckDB and GCC for pg_duckdb; Trixie supplies Clang. The final CNPG
extension image contains the extension payload rather than a complete PostgreSQL
server.

## SBOM contents

The shared generator records shipped files and OS package ownership. The
recipe-owned hook adds pg_duckdb, DuckDB and bundled components
selected from the shipped shared library's build inputs. Examples include fmt, yyjson,
cpp-httplib, miniz, utf8proc, LZ4, Zstandard, Brotli, Mbed TLS and FSST. The image
also contains generated Unicode, CLDR and IANA time-zone data. The upstream
extension named `icu` uses its own implementation and generated data; that name
alone does not establish a linked ICU library.

Versions come from selected source headers and release metadata where available.
Modified snapshots retain source URLs identifying their revision and vendor path.
Unknown release versions are omitted from SPDX `versionInfo`; commit/path strings
are not synthesized as versions. DuckDB's reported version override is recorded
separately from its source identity. The attached SBOM contains these identities;
this document does not duplicate their pins.

The shared system-library helper stages additional runtime libraries under
`/system`, excluding libraries supplied by the PostgreSQL base image, and preserves
their notices. `evidence.py` stages the extension library/SQL payload and
original notices. `augment_spdx.py` preserves the generator's existing records
and adds source evidence through its hook interface. Builder reports are private
validation inputs; consumers use the standard SPDX document described in the
[shared dependency guidance](../../source-build/README.md#dependency-evidence-in-the-sbom). Neither is a generic
Universe dependency or license helper. Source-input relationships do not prove
that every object survives linker dead-code elimination.

Vendor and generated-data notices are shipped under `/licenses`. Composite
terms retain their complete text through LicenseRefs. Review component identities,
notice sources and applicable obligations when updating the release; missing or
unresolved license information does not itself establish compliance with the
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
