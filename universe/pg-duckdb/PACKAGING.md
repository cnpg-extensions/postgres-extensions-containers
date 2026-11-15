# pg_duckdb packaging notes

## Debian packaging obstacles

The recipe follows the selected release's upstream Docker image build: pg_duckdb
links dynamically to its pinned DuckDB fork. A stock DuckDB development package
does not establish compatibility with that fork's interfaces. Debian packaging
would require coordinated packaging of the fork and its bundled dependencies,
or unbundling patches. Namespace-modified code, such as DuckDB's LZ4, adds to
that work. Ordinary dependencies use Debian packages.

The build uses upstream's default release settings, Clang for DuckDB and GCC for
pg_duckdb, with the Clang version supplied by Trixie. The final CNPG extension
image contains the extension payload rather than a complete PostgreSQL server.
Revisit Debian packaging when the fork and bundled-dependency burden is resolved.

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
