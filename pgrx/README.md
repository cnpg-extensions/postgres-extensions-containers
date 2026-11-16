# PGRX extensions

These PostgreSQL extension images use PGRX, a framework for writing PostgreSQL
extensions in Rust. They can be loaded into CloudNativePG without installing a
Rust toolchain in your database container.

Start with the [quick start](../README.md#quick-start): set up extension-update
email alerts first, then use the CronJob to install and refresh the catalog. Select extensions
by name to inherit their image references and runtime settings from the catalog.

See the [supported extensions](../README.md#supported-extensions) in the top-level
README for the extension list and links to usage instructions.

Each extension's README lists its supported PostgreSQL versions and distributions,
Cluster and Database configuration, and any required preload or initialization
settings. Use those instructions to add the image and enable the SQL extension.

## Image information

Images carry SBOM and provenance attestations, with original license notices
inside the image under `/licenses`.
See [image verification and SBOM inspection](../README.md#verify-images)
for consumer instructions. PGRX SBOMs include the configured Rust dependency graph;
this does not mean every dependency survives linker dead-code elimination.

## Contributing

For recipe development and local builds, see the
[source-build guide](../source-build/pgrx/README.md).
