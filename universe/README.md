# Universe source builds

Recipes whose dependency burden makes Debian packaging prohibitive live here.
Ordinary extensions should use Debian packaging; PGRX extensions use `pgrx/`.
Inclusion requires a concrete dependency-packaging rationale, accurate shipped
component identities in the SBOM, and the shared acceptance checks.

Use the [shared source-build guide](../source-build/README.md) for native
AMD64/ARM64 compilation, image verification, release stages and local validation.
The [pg-duckdb recipe](pg-duckdb/README.md) documents its packaging rationale,
source evidence, payload and runtime requirements.
