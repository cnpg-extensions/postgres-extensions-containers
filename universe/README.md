# Universe extensions

Universe contains PostgreSQL extension images with complex bundled dependencies.
These images use the same CloudNativePG installation mechanism as the other
extensions in this repository.

See the [supported extensions](../README.md#supported-extensions) in the top-level
README for the extension list and links to usage instructions.

Follow the extension's README for supported versions, Cluster and Database
configuration, preload requirements and runtime caveats.

## Image information

Images include an SBOM, provenance and original license notices under `/licenses`.
See [image verification and SBOM inspection](../README.md#verify-images)
for consumer instructions. The [pg_duckdb packaging notes](pg-duckdb/PACKAGING.md)
summarize its bundled components and Debian packaging rationale.

## Contributing

For recipe development and local builds, see the
[source-build guide](../source-build/universe/README.md).
