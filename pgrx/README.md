# PGRX extensions

These PostgreSQL extension images use PGRX, a framework for writing PostgreSQL
extensions in Rust. They can be loaded into CloudNativePG without installing a
Rust toolchain in your database container.

See the [supported extensions](../README.md#supported-extensions) in the top-level
README for the extension list and links to usage instructions.

Each extension's README lists its supported PostgreSQL versions and distributions,
Cluster and Database configuration, and any required preload or initialization
settings. Use those instructions to add the image and enable the SQL extension.

## Image information

Images include an SBOM, provenance and original license notices under `/licenses`.
See [image verification and SBOM inspection](../source-build/README.md#verify-images)
for consumer instructions. PGRX SBOMs include the configured Rust dependency graph;
this does not mean every dependency survives linker dead-code elimination.

## Contributing

For recipe development and local builds, see the
[source-build guide](../source-build/pgrx/README.md).
