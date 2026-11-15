# pg_duckdb packaging notes

## Debian packaging obstacles

The selected release's [compilation guide](https://github.com/duckdb/pg_duckdb/blob/v1.2.0/docs/compilation.md)
describes `ReleaseStaticSystem`: pg_duckdb embeds its pinned DuckDB fork and
matching httpfs through private static archives and generated registration
objects. A stock DuckDB development package does not provide that exact interface.
Debian packaging would require coordinated packaging of the fork and httpfs, or
unbundling patches that replace this integration. Namespace-modified bundled
code, such as DuckDB's LZ4, adds to that work.

Ordinary dependencies use Debian packages, including OpenSSL, curl and the LZ4
used for PostgreSQL TOAST. Their availability does not resolve the embedded
engine's packaging burden. Revisit Debian packaging when that burden is resolved.

## SBOM contents

The shared generator records shipped files and OS package ownership. The
recipe-owned hook adds pg_duckdb, embedded DuckDB, httpfs and bundled components
selected from the static-link build inputs. Examples include fmt, yyjson,
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

`evidence.py` stages the library/SQL payload, required runtime libraries and
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

`acquire.py` owns the repository URL, resolves `EXT_VERSION` during acquisition,
and downloads that commit and its matching nested sources. Preparation does not
freeze tags across platforms: a moved tag can select different commits in
separate builds. BuildKit can reuse a cached acquisition for an unchanged recipe
and version; invalidate that cache when a fresh tag lookup is needed. This recipe
needs private revision resolution for correct nested acquisition, without adding
a public source-identity schema or a cross-platform consistency gate.
