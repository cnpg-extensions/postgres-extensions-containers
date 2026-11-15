# PGRX extensions

These PostgreSQL extension images use PGRX, a framework for writing PostgreSQL
extensions in Rust. They can be loaded into CloudNativePG without installing a
Rust toolchain in your database container.

## Available extensions

| Extension | Purpose |
| --- | --- |
| [pg_durable](pg-durable/README.md) | Durable SQL workflows. |
| [pg_graphql](pg-graphql/README.md) | GraphQL queries over PostgreSQL schemas. |
| [pg_jsonschema](pg-jsonschema/README.md) | JSON Schema validation. |
| [pg_parquet](pg-parquet/README.md) | Read and write Parquet files. |
| [pg_search](pg-search/README.md) | Full-text, faceted and hybrid search. |
| [pg_session_jwt](pg-session-jwt/README.md) | JWT verification and session claims. |
| [pglinter](pglinter/README.md) | Database schema and configuration checks. |
| [PostgreSQL Anonymizer](postgresql-anonymizer/README.md) | Anonymization and data masking. |

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
