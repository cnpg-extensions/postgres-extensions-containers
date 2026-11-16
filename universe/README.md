# Universe extensions

Universe contains PostgreSQL extension images with complex bundled dependencies.
These images use the same CloudNativePG installation mechanism as the other
extensions in this repository.

Start with the [catalog quick start](../README.md#quick-start), including
extension-update email alerts and scheduled weekly maintenance. Select extensions
by name to inherit their image references and runtime settings from the catalog.

See the [supported extensions](../README.md#supported-extensions) in the top-level
README for the extension list and links to usage instructions.

Follow the extension's README for supported versions, Cluster and Database
configuration, preload requirements and runtime caveats.

## Image information

Images carry SBOM and provenance attestations, with original license notices
inside the image under `/licenses`.
See [image verification and SBOM inspection](../README.md#verify-images)
for consumer instructions. The [pg_duckdb packaging notes](pg-duckdb/PACKAGING.md)
summarize its bundled components and Debian packaging rationale.

## Contributing

For recipe development and local builds, see the
[source-build guide](../source-build/universe/README.md).
