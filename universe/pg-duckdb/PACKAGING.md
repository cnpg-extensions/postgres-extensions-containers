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

The recipe follows Debian DuckDB's package boundaries: one `libduckdb2.0`
record, seven library records and a separate upstream pg_duckdb record. Internal
components such as RE2, jemalloc, fmt, miniz and Parquet remain covered by DuckDB.
The eight library records use Debian unstable's binary and source package names,
with `pkg:deb/debian` identifiers, to enable Debian vulnerability matching.

**Versions describe the upstream code actually compiled.** They do not use the
current unstable binary versions, invent Debian revision suffixes, or claim
Debian security patches were applied. The compiled Clang configuration selects
Snappy 1.2.1; GCC would select a different bundled Snappy version and requires
an inventory review. Source URLs and the fact that these are source-built
scanner mappings, not dpkg-installed binaries, are retained in `sourceInfo`.

### Copyright snapshot and version mapping

The following copyright files were copied once from Debian unstable source
packages on 2026-11-15. Source archives were checked against the archive index's
SHA256 values. The copyright files are checked in verbatim and copied to
`/licenses/<Debian-binary-package>/copyright`, matching the system-library
helper's directory layout. The copyright source version is provenance for the
notice document, **not** the version reported for our compiled library.

| Package / checked-in copyright | Compiled version in SBOM | Copyright source package |
|---|---|---|
| [libduckdb2.0](licenses/libduckdb2.0/copyright) | 2.0.0 | [duckdb 2.0.0+dfsg2-1](https://deb.debian.org/debian/pool/main/d/duckdb/duckdb_2.0.0+dfsg2-1.debian.tar.xz) |
| [libbrotli1](licenses/libbrotli1/copyright) | 1.1.0 | [brotli 1.2.0-4.1](https://deb.debian.org/debian/pool/main/b/brotli/brotli_1.2.0-4.1.debian.tar.xz) |
| [liblz4-1](licenses/liblz4-1/copyright) | 1.9.4 | [lz4 1.10.0-10](https://deb.debian.org/debian/pool/main/l/lz4/lz4_1.10.0-10.debian.tar.xz) |
| [libmbedcrypto16](licenses/libmbedcrypto16/copyright) | 3.6.7 | [mbedtls 3.6.7-3](https://deb.debian.org/debian/pool/main/m/mbedtls/mbedtls_3.6.7-3.debian.tar.xz) |
| [libsnappy1v5](licenses/libsnappy1v5/copyright) | 1.2.1 | [snappy 1.3.1-4](https://deb.debian.org/debian/pool/main/s/snappy/snappy_1.3.1-4.debian.tar.xz) |
| [libyyjson0](licenses/libyyjson0/copyright) | 0.9.0 | [yyjson 0.12.0+ds-2](https://deb.debian.org/debian/pool/main/y/yyjson/yyjson_0.12.0+ds-2.debian.tar.xz) |
| [libzstd1](licenses/libzstd1/copyright) | 1.5.6 | [libzstd 1.5.7+dfsg-4](https://deb.debian.org/debian/pool/main/libz/libzstd/libzstd_1.5.7+dfsg-4.debian.tar.xz) |
| [libxxhash0](licenses/libxxhash0/copyright) | 0.6.2 | [xxhash 0.8.3-2](https://deb.debian.org/debian/pool/main/x/xxhash/xxhash_0.8.3-2.debian.tar.xz) |

The build copies pg_duckdb's own LICENSE and NOTICE into
`/licenses/pg_duckdb/copyright`. Referenced Debian common-license texts are
included alongside the relevant copyright files. These source-package copyright
files can describe tests, tools and documentation beyond the shipped library;
they are not an inventory of additional runtime components.

There is no license extraction script, build-time copyright download, dependency
discovery or comment parser. `evidence.py` has one static package table. Both
source-revision guards require the inventory and copyright snapshot to be
reviewed when sources or build settings change.

### Scanner interpretation and file ownership

Each Debian PURL records architecture, `distro=debian-unstable` and the Debian source
package name (`upstream`), including mappings such as `libzstd1` to `libzstd`.
Scanners must support that Debian distribution and source-package mapping.
Debian advisory results are comparisons against Debian's version rules, not
proof that an upstream-built binary has Debian's patch set or that every
embedded component has been independently scanned. In particular, a bare upstream
version can compare earlier than a Debian revision containing that same upstream
release, and a source-package advisory can concern code this library does not
include. Matches require applicability review.

The shared generator still inventories every shipped file. Copied copyright or
common-license files can cause it to select an installed builder package even
when none of that package's binary files ship. The hook replaces only records
whose entire shipped-file ownership consists of these mapped notices. Packages
owning actual shipped binaries remain intact, including distinct system and
embedded copies of the same library. Notice relationships and complete extracted
license text are retained under the explicit compiled-version records.

The PostgreSQL 18/Trixie amd64 build uses five Debian library packages from its
base image: libc6, libgcc-s1, libstdc++6, liblz4-1 and libxxhash0. pg_duckdb links
to system LZ4, which links to system xxHash; the source-built DuckDB library
contains separate embedded copies. Only source-built libduckdb.so is staged as
an additional shared library. Thus the eight Debian-style SBOM identities do
not mean that eight Debian binary packages were installed into this payload.
Upstream's loadable httpfs is not shipped here; its curl/OpenSSL build
requirements must not become runtime inventory entries just because apt
installed them in the builder.

The final image copies the installed extension into `/lib` and `/share`, plus
`/system` and `/licenses`; there is no intermediate `/payload`. Consumers use
the standard SPDX document described in the
[shared dependency guidance](../../source-build/README.md#dependency-evidence-in-the-sbom).
The original native build passed PostgreSQL preload, `CREATE EXTENSION` and a
forced `DuckDBScan` query. Follow-up SBOM checks reuse that compiled amd64 builder;
they do not establish fresh compilation, ARM64 or hosted signing/SLSA acceptance.
The local checks passed 43 shared tests, verified all eight copyright copies
against their Debian source archives, and exercised the actual BuildKit SPDX
through Grype. A separate known-vulnerable LZ4 fixture confirmed Debian advisory
matching; scanner matches on the real document still require applicability review.

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
