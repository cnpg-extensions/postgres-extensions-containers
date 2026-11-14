# pg-duckdb pilot

Maintainer: [@ardentperf](https://github.com/ardentperf).
Targets: PostgreSQL 18 / Trixie, native linux/amd64 and linux/arm64.

## Selected release and evidence

GitHub's latest stable release API returned `v1.2.0`, commit
`8756099e267c47f0b86c24de4cf995327f1f4279`. This release's control file declares
SQL version `1.2.0` and its SQL directory supplies that installation script and
upgrade scripts. Stripping `v` is verified for this release; later releases
require control/upgrade review.

Its DuckDB gitlink is `d54cbbe3df17e8e5ce68312f483b4155836112aa`.
The pg_duckdb Makefile overrides DuckDB's reported version to `v2.0.0`;
that does not establish equivalence to a stock DuckDB 2.0.0 release. Evidence
retains the override and exact revision, with a revision-qualified DuckDB PURL.
httpfs is pinned by `third_party/pg_duckdb_extensions.cmake` to
`77392a72077a85897db2519fae11e2c0da972b8a`. Acquisition derives both nested pins
from selected source, fetching HTTPS archives. The sole build adaptation replaces
httpfs Git acquisition with equivalent local SOURCE_DIR / EXTENSION_VERSION;
a marker satisfies the archive build's Makefile gitlink prerequisite.

## Debian dependency packaging obstacles

[The selected release's compilation guide](https://github.com/duckdb/pg_duckdb/blob/v1.2.0/docs/compilation.md)
supports PG18 and `ReleaseStaticSystem`. The Makefile statically embeds DuckDB,
json, icu and httpfs, linking internal archive objects and generated static
registration objects. httpfs must match that DuckDB extension ABI. DuckDB carries
namespace-modified bundled sources (including `duckdb_lz4`). Substituting Debian
shared libraries requires unbundling patches, packaging the exact DuckDB fork
and matching httpfs interface together, and maintaining independent license and
security tracking for the embedded libraries. Availability of a distribution
DuckDB package alone would not satisfy these internal-linkage requirements.

`ReleaseStaticSystem` uses Debian OpenSSL/curl and system LZ4 for PostgreSQL TOAST;
it still embeds DuckDB's own LZ4. This avoids the vcpkg-built OpenSSL/curl stack
of `ReleaseStatic`. These ordinary dependencies alone do not justify Universe.
Trixie already packages [OpenSSL](https://packages.debian.org/trixie/libssl-dev),
[curl](https://packages.debian.org/trixie/libcurl4-openssl-dev), and
[LZ4](https://packages.debian.org/trixie/liblz4-dev); PostgreSQL 18 development
packages are available in [PGDG](https://apt.postgresql.org/pub/repos/apt/pool/main/p/postgresql-18/).
[Debian's DuckDB development-package search](https://packages.debian.org/search?keywords=libduckdb-dev)
lists forky/sid, not Trixie. Package availability alone does not resolve the exact
DuckDB gitlink, matching httpfs pin, and private static registration interface.

Revisit Debian packaging when the fork/ABI/unbundling burden is resolved.

This DuckDB revision's `extension/icu/README.md` explicitly says it no longer
uses ICU: it has its own calendar/collation implementation and generated
Unicode/time-zone data. Do not infer a linked ICU package from the name.

## Payload and SBOM contract

The scratch payload contains `/lib/pg_duckdb.so`, `/share/extension/pg_duckdb*`,
the ELF dependency closure in `/lib`, and original notices in `/licenses`.
The builder retains dpkg ownership records for the shared generator. The hook
at `/usr/local/share/cnpg-sbom/augment_spdx.py` implements API v1 and reads
`/build/universe-evidence.json`. It binds evidence to final file hashes and
preserves the generator's file inventory and OS packages; it is not a composer.

Vendor versions are extracted at evidence-generation time from the selected
headers: fmt's packed `FMT_VERSION`, yyjson and cpp-httplib string macros,
miniz's source-version banner (not its zlib-compatibility `MZ_VERSION`), and
utf8proc/LZ4/Zstandard/Brotli numeric version macros.
For the selected sources these yield 6.1.2, 0.9.0, 0.53.1, 2.0.8, 2.9.0,
1.9.4, 1.5.6 and 1.1.0 respectively. Their canonical GitHub PURLs survive
composition. Mbed TLS uses its VERSION file; FSST's README records upstream
commit `0f0f9057048412da1ee48e35d516155cb7edd155`. Other vendors retain canonical
project names (including FastPFor, Redis HyperLogLog, pcg-cpp, parquet-format,
thrift and t-digest) with the exact enclosing source revision and vendor path.
These are modified snapshots, not inferred upstream releases. Vendored PostgreSQL
ruleutils/utility code is represented separately at its pg_duckdb source revision;
the installed PostgreSQL development package supplies its redistribution terms. Snappy's header
contains compiler-dependent 1.2.1/1.1.7 branches, so its source revision is retained
rather than reporting one version for every compiler. No guessed CPE is emitted.

The Ninja transitive inputs of the static link archives and registration objects
select compilation units and their recorded header dependencies. This includes
extension archives, httplib and loadable-extension support outside
libduckdb_static.a; compiler/test targets do not establish runtime inclusion.
This remains source-input evidence rather than proof of linker dead-strip output.

Generated tables identify IANA tzdata 2026e, CLDR 48 and UCD 17.0.0. The generation
scripts identify Unicode's ICU-data redistribution and CLDR/UCD sources.
Evidence staging retrieves the original [ICU-data notice](https://github.com/unicode-org/icu-data/blob/6eac2f4d349d9f4a0825103bb41845d8e5ab7add/LICENSE),
[CLDR 48 notice](https://github.com/unicode-org/cldr/blob/release-48/LICENSE), and
[Unicode data license](https://www.unicode.org/license.txt), retaining their URLs
and complete bytes in the payload. Notice retrieval fails the staging step on
network/HTTP errors; the UCD license URL is the Unicode project’s current notice. The ICU-data notice includes IANA's public
domain statement; Unicode's redistribution must not be labeled MIT. CLDR/UCD
use Unicode-3.0; composite ICU-data terms retain a LicenseRef.

Original vendor license files and leading source notices are preserved, including
Redis HyperLogLog's BSD terms absent from its directory's MIT LICENSE. Composite
terms retain complete text in LicenseRefs instead of being collapsed to the first
recognized license. The selected-release guard requires review of source identities
and generated-data notice URLs when updating. Missing notices remain explicit
NOASSERTION and license-policy acceptance remains integration work.

Hook fixtures verify source identities, preservation of scanned packages/files and
ownership, extracted composite notices, and rejection of payload notice loss.
These are local fixtures, not attached architecture SBOM validation.

## Initialization and permissions

Preload `pg_duckdb` using `shared_preload_libraries`, restart PostgreSQL, then
`CREATE EXTENSION pg_duckdb` as superuser. The PostgreSQL runtime user needs
read/execute access to libraries and read access to SQL files. Keep the payload
read-only. Writable paths default to `$PGDATA/pg_duckdb/temp` and
`$PGDATA/pg_duckdb/extensions`, configurable by the superuser with
`duckdb.temporary_directory` and `duckdb.extension_directory`. Optional downloaded
extensions are outside the image SBOM; json/icu/httpfs are embedded here.
DuckDB execution defaults to superusers; `duckdb.allowed_role` can delegate it,
including access to secrets. Local filesystem access follows upstream server-file
role checks. See this release's `docs/settings.md` before granting access.

## Build and validation

From repository root, on a native AMD64 worker (ARM64 uses `linux/arm64`):

```sh
docker buildx build --platform linux/amd64 \
  --build-arg PG_MAJOR=18 --build-arg EXT_VERSION=v1.2.0 \
  --build-arg SOURCE_REPOSITORY=https://github.com/duckdb/pg_duckdb \
  --build-arg SOURCE_REVISION=8756099e267c47f0b86c24de4cf995327f1f4279 \
  --build-arg BUILD_TIMESTAMP="$(date -u +%FT%TZ)" \
  --sbom=generator=ghcr.io/cnpg-extensions/cnpg-sbom-generator:latest@sha256:9909ad887161b18d68f1e84c5568be3e8d3072ad861be843b596a0fdb6c48678 \
  -f universe/pg-duckdb/Dockerfile .
```

Use the [shared native-worker preflight, preparation and local validation
guide](../../source-build/README.md#development). The recipe uses the ordinary
shared smoke tests; it has no extension-specific runtime suite. Runtime libraries
require `ld_library_path = ["lib"]` so PostgreSQL can find the bundled closure,
including libcurl.

Build evidence must retain DuckDB/httpfs revisions, canonical versions and PURLs,
dpkg ownership and Syft records, original notices, and payload hash binding in
each architecture's final SBOM. Compiler-only inputs must not be reported as
shipped packages. Keep miniz's source version distinct from its compatibility macro.

CI uses the shared security action. Optional local vulnerability and license
reports use the [consumer verification commands](../../source-build/README.md#verify-images).
Renovate tracks stable upstream GitHub releases and opens source-update PRs;
SQL mappings and bundled-source evidence require review before those updates merge.
