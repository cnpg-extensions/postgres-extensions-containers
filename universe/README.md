# Universe source builds

Recipes whose dependency burden makes Debian packaging prohibitive live here.
Ordinary extensions should use Debian packaging; Rust extensions use the PGRX path.
Inclusion requires a concrete dependency-packaging rationale, accurate shipped
component identities in the SBOM, and the shared acceptance checks.

Start with the [source-build templates and utility guide](../source-build/README.md#add-a-universe-recipe).
Each recipe supplies its own compilation, runtime dependency and license evidence
handling. Universe has no equivalent of the automatic PGRX Cargo helpers.

The extension README documents installation and use. A separate `PACKAGING.md`
explains the Debian packaging obstacles and summarizes SBOM contents; see
[pg-duckdb](pg-duckdb/PACKAGING.md) for an example.

## Dependency evidence in the SBOM

The final SPDX SBOM must include shipped dependencies, including bundled and
statically linked components that automatic scanning misses. Each dependency
must use its canonical upstream or ecosystem package name, including the name
used by vulnerability advisories where applicable. This matters even when no CVE
exists today: future advisories should be matchable to the shipped component.
Do not substitute a recipe-local nickname for an established package identity.
Matching still depends on scanner and advisory support. Unknown versions can
broaden scanner matches as well as reduce coverage; missing identifiers can also
limit automated matching.

Use established SPDX fields and Package URL types:

- Record the actual upstream version when known. Omit optional `versionInfo`
  when unknown; do not invent versions from repository commits and source paths.
  Distinguish source versions from API compatibility macros.
- Include an accurate standard PURL when the component's ecosystem and source
  support one. Do not guess registry membership, CPEs, versions or identifiers
  merely to satisfy a scanner. Preserve canonical names when a reliable PURL is
  unavailable, and explain unresolved identity evidence in the recipe's packaging notes.
- Express dependency relationships using standard SPDX relationships. Keep
  distinct components distinct, including forks with the same name and version.
- Preserve shipped-file inventory, runtime package ownership, checksums, license
  expressions and original attribution/notices. Use SPDX `LicenseRef` and
  extracted licensing information for terms without an applicable SPDX license
  identifier. Associate required redistribution notices with the standard
  `DISTRIBUTION_ARTIFACT` relationship.

Use the shared generator's existing augmentation hook for missing source-built
components. Evidence must describe the selected sources and final payload;
validate their binding during the build. Builder reports and recipe helpers are
private implementation details, not a second consumer schema. Do not publish
custom JSON annotations, identifier qualifiers, sidecars or attestations as an
alternative API. SPDX identifiers and document namespaces are opaque;
`sourceInfo` is optional human-readable context, not a parseable contract.

Source attribution remains available through recipes, standard source links and
ordinary build provenance where captured. Exact source commit recovery is not a
prerequisite for every build. Tags may move and acquisition may be cached; a
build timestamp alone does not prove which commit a tag selected. Recipes may
resolve commits privately when required to acquire matching nested dependencies.
This does not introduce a new public source-identity contract.
