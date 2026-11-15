# Universe source builds

Recipes whose dependency burden makes Debian packaging prohibitive live here.
Ordinary extensions should use Debian packaging; Rust extensions use the PGRX path.
Inclusion requires a concrete dependency-packaging rationale, accurate shipped
component identities in the SBOM, and the shared acceptance checks.

For published images, use the shared [image verification and SBOM inspection
guide](../source-build/README.md#verify-images).

Start with the [source-build templates and utility guide](../source-build/README.md#add-a-universe-recipe).
Each recipe supplies its own compilation, runtime dependency and license evidence
handling. Universe has no equivalent of the automatic PGRX Cargo helpers.

The extension README documents installation and use. A separate `PACKAGING.md`
explains the Debian packaging obstacles and summarizes SBOM contents; see
[pg-duckdb](pg-duckdb/PACKAGING.md) for an example.
