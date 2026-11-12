# Development approach

## Project priority: track upstream

Tracking the CloudNativePG upstream project is a high-priority goal. Preserve
upstream alignment and keep intentional downstream differences explicit.
Choices inherited from upstream do not need separate justification or entries
in the local workaround register; this includes the inherited OpenTelemetry
dependency overrides.

Use the mainline Debian build process as the baseline for PGRX work. Prefer its
existing actions, conventions, metadata formats, and shared release/test
infrastructure. Borrow patterns from the SBOM generator when they solve a need
that the Debian path does not cover. Avoid creating a parallel framework where
existing project behavior is sufficient.

Minimize avoidable conflicts with future upstream merges. Prefer small,
localized changes and preserve upstream file and job structure where practical.
When refactoring shared infrastructure, weigh reuse against the ongoing cost of
reconciling upstream changes. A clean merge still requires behavioral review
across downstream implementations.

Review upstream changes for behavioral applicability, even when Git merges
cleanly. Distinguish pending upstream updates from intentional downstream
choices. Record actual source workarounds and their removal conditions, rather
than documenting inherited choices as new exceptions.

Keep Debian and PGRX on the shared CNPG support policy in
[cnpg-versions.yml](.github/workflows/cnpg-versions.yml), with one Renovate-managed
latest-release pin. This logic was extracted from Debian's `bake_targets.yml`;
when upstream changes its version selection, apply the same intent to the shared
workflow rather than creating a separate PGRX support matrix. Follow the
[upstream merge process](MERGE.md).

Keep PGRX release acceptance aligned with Debian: build-time validation,
security scanning, signing, shared runtime smoke tests, and required SLSA jobs.
Do not add repeated full OCI-graph verification or per-field BuildKit provenance
comparisons against preparation records to these stages. Keep independent
[consumer verification](pgrx/README.md#verify-images) available.

## Keep orchestration small

Set up tools where they are needed. Prefer standard setup actions and the SBOM
generator's container-based Grype/Grant scanning pattern over a central workflow
tool installer. Keep Rust build-tool installation inside the extension builder.

Prefer ordinary Bake metadata and direct immutable image references over custom
record envelopes, copied identity fields, whole-workspace hashes, and repeated
self-checksums. Simplify producers and consumers together, including workflow
jobs and artifact handoffs. Do not remove a check merely because it is custom:
retain checks that prevent incorrect or incomplete published output.

Use trusted upstream HTTPS source archives and record what was actually built.
Do not reintroduce preparation-time archive checksum enforcement or
cross-platform source-consistency machinery that was intentionally removed.
Keep useful source evidence, lockfile guards for actual recipe workarounds,
and ordinary build-time validation.

Keep the shared SBOM generator and its extension hook interface. Preserve runtime
package selection, ownership, shipped-file inventory, license attribution, and
scanning of both architectures' SPDX documents. Do not introduce a second SBOM
composer or a PGRX-specific interface for image consumers.

## Testing philosophy

Prioritize tests for realistic mistakes that could pass the build while producing
incorrect or incomplete results, especially package inventory, ownership, licenses,
and downstream hook output. Avoid duplicating failures that the build already
reports with a debuggable error, or testing third-party validators themselves.
Keep build-time validation and end-to-end integration checks.

Avoid hard-coded extension inventories or fixed matrix-size assertions that need
editing whenever an extension is added. Test the discovery and selection behavior
and the completeness of its output instead.

Run checks appropriate to the change. Exercise real Docker/BuildKit, registry,
and scanner paths when changing their integration. Documentation-only edits need
link, formatting, and accuracy checks rather than a full rebuild. Report exactly
what passed and distinguish local fixtures, existing compiled builders, fresh
native builds, and hosted release validation. Do not imply that local tests cover
GitHub signing, SLSA, or native ARM64 compilation when they did not.

## Commit trailers

Every commit must include a DCO `Signed-off-by` trailer (`git commit -s`).
AI-assisted commits must also include an `Assisted-By` trailer naming the
assistant and model, for example `Assisted-By: OpenAI Codex (GPT-6.1-Sol)`.
