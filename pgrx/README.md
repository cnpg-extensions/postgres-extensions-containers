# PGRX extension builds

PGRX targets are discovered from `build_system = "pgrx"` in ordinary extension
metadata. Debian discovery and OS-library maintenance exclude those targets;
catalog and testing-value generation support both. Source tags remain literal
(including `v`), while SQL versions remain separate. Extension READMEs describe
usage; this directory contains build and validation internals.

Consumers use the shared [verification procedure](VERIFYING_IMAGES.md) for all
extension images.

## Build and evidence contract

The extension Dockerfiles retain their attributed upstream build commands.
`install-pgrx-build-environment.sh` runs `apt-get update` and `apt-get install`
for Debian build dependencies, then installs the Renovate-managed Rust and tool
versions. Rustup installs the selected compiler using its normal distribution
verification; reporting binaries come from versioned upstream releases. The
cargo-pgrx version comes from the upstream extension Cargo.lock and is installed
through Cargo with that exact version and its locked dependencies.
The JWT Dockerfile corrects v0.5.0's package version with an inline sed command
guarded by exact original and effective Cargo.lock checksums. Anonymizer 3.3.2
similarly corrects its stale root Cargo.lock version with exact checksums. Any
upstream lock change requires reviewing or removing the affected correction.
The installer records both original and effective lock hashes; the legacy
`patches` evidence field remains empty for schema compatibility. Cargo-about
and other release tools use architecture-specific artifacts resolved from their
Renovate-managed versions. Only cargo-pgrx is built from source. All locked crate
sources are fetched before offline reporting because cargo-about queries
metadata before applying its target filter.
Preparation resolves each metadata source tag to a repository revision and
archive, then freezes the archive hash and source identity for the native jobs.
The build records the upstream Cargo.lock hash and derives cargo-pgrx from that
lock; these generated inputs are not maintained in a separate committed lock.

The post-build finalizer resolves target-filtered Cargo metadata using the same
package, PostgreSQL feature, non-PG defaults, and feature policy as cargo-pgrx.
It emits Cargo metadata and cargo-about reports, checks Cargo.lock for drift, ships
license texts, and hashes the finished library/control/SQL payload. The manifest
uses evidence schema v2 and is written last. The diagnostic `pgrx-sbom` target exports these reports; it does
not replace an attestation-producing image build.

The published, digest-pinned CNPG generator runs unchanged. Its API-v1 hook reads
hashed reports from the builder mount and verifies target and source identity.
It reruns the generator image's Syft binary with `rust-cargo-lock-cataloger` on a
`file:` source containing only the hash-verified extension Cargo.lock. The scan
cannot discover cargo-about, cargo-pgrx, or cached registry lockfiles elsewhere in
the builder. Its version, output hash, and inventory count are recorded in the
augmentation annotation; the generator image digest owns the Syft version.
The hook selects runtime crates using Cargo metadata, matches each selected name,
version, and source to that Syft inventory, and emits only the selected entries.
It excludes build/dev and proc-macro-only edges, and binds the reported root to
identical final payload bytes and ELF machine.
Runtime features propagate from the selected root through active dependencies;
weak optional feature references do not activate unused backends or leak their
features into shared crates. Cargo metadata supplies full package identities;
retained dependency conditions are evaluated against `rustc --print cfg` for
the selected target. Generated Python bytecode is excluded from Docker
contexts so local reporting caches cannot change the copied helper code.
It preserves the generator's final-file inventory, retained Syft packages,
checksums, relationships, and license metadata. Syft packages survive composition
only when they own shipped files; builder-only packages and the builder's OS
identity are not added to the final document. The hook runs once on the current
generator output; it does not support historical synthetic-package output or
preexisting Cargo packages. The selected root Cargo package is the document's
described extension component and has its own Cargo identity; it `DEPENDS_ON`
the selected Rust packages.
Cargo packages do not claim file-level analysis or own installed files. The `.so`,
control and SQL files, and bundled license notices remain individual SPDX file
records with checksums and any license metadata supplied by Syft. The hook does
not infer file licenses from Cargo declarations or shipped notice text. The
notices remain in the image for distribution and compliance needs. Cargo package
license expressions come uniformly from cargo-about, preserving AND/OR semantics. Missing, unknown or invalid expressions for selected crates
fail the build. License texts remain in the SPDX document and shipped notices
are attributed to crate entries by full Cargo identity. The generator performs
full SPDX validation after the hook returns; the standalone artifact verifier
also checks downloaded document structure.
cargo-about 0.9.2's repeated,
identical Boolean `doctest` field is normalized before report hashing. Other
duplicate JSON keys and conflicting values are rejected.

Preparation freezes the source snapshot, timestamp, generator, resolved source
identities and hashes, base indexes, targets, and definitions for a logical
workflow run. Each base index resolves to its architecture-specific child
manifest. Every native platform job builds one target on its matching
architecture and records the actual source, base child, and build evidence. It
exports a complete OCI layout and a record bound to that preparation. Assembly
rejects missing or unexpected records,
validates their raw graphs, and uses full staging-index references in Buildx's
dry-run merge. Normal tags are assigned only after reading back a valid candidate.

Sign, security, smoke, and promotion consume per-target assembly artifacts.
The shared reusable SLSA generator attests each assembled testing index; its
success gates promotion. After promotion, the same generator attests each index
in its production repository. Production promotion is restricted to trusted
`main` push/dispatch events.
Grype reports vulnerabilities and Grant reports licenses; findings are retained for review,
while scanner errors fail the job. Both build paths use the shared CNPG support
policy: `main`, the highest stable patch of the previous minor, and the pinned
latest release. Smoke uses the shared Taskfile's live operator manifests and
catalogs, including development images for `main`.
The smoke uses the shared Task/Dagger setup, CNPG extension catalogs, and
extension installation checks. The pg-search recipe
captures base libraries before installing packages, then stages the packaged
extension's additional runtime closure and copyright notices using the shared
helpers. This includes quadmath where required.

## Local validation

The dedicated PGRX contract workflow runs independently of Go tests. It does not
replace the shared Automerge gate or change branch protection.

Run from the repository root with Docker Buildx, Go, Dagger, actionlint, and
Python available. The Python tests also run Syft against fixture lockfiles. Signing and full extension acceptance run in GitHub Actions
on native AMD64 and ARM64 runners; no local signing keys are needed.

Create and activate a virtual environment for SPDX validation, then copy Syft
from the same pinned generator used by the workflow:

```sh
python3 -m venv /tmp/cnpg-pgrx-venv
source /tmp/cnpg-pgrx-venv/bin/activate
spdx_tools_version=$(sed -n 's/^ARG SPDX_TOOLS_VERSION=//p' sbom-generator/Dockerfile)
test -n "$spdx_tools_version"
python -m pip install "spdx-tools==${spdx_tools_version}"
generator=$(sed -n 's/^ *SBOM_GENERATOR: //p' .github/workflows/pgrx_targets.yml)
test -n "$generator"
syft_container=$(docker create "$generator")
docker cp "$syft_container:/usr/local/bin/syft" "$VIRTUAL_ENV/bin/syft"
docker rm "$syft_container"
```

Run all local unit, workflow, and dependency checks once:

```sh
task pgrx:validate
# Optional: also exercise the pinned Renovate extraction and replacements.
task pgrx:validate -- --renovate-output /tmp/pgrx-renovate-check
```

For a quick downstream-only check, use `task pgrx:test`. CI runs this suite
inside the pinned generator image so Syft and the SPDX validator match the
production hook environment. The generator's
BuildKit/SPDX/Grype/Grant integration fixture is maintained in
`sbom-generator/tests/integration/`; its workflow runs it on both native
architectures.

For full extension acceptance, dispatch `.github/workflows/pgrx.yml` with an
`extension_name`. It builds all metadata-declared targets on native AMD64 and
ARM64, assembles and signs their indexes, checks SPDX/Grype/Grant results, and runs
CNPG smoke tests. Branch builds publish testing packages; production promotion
requires a trusted `main` event. An optional `cnpg_version` selects `main` or a full version such as `1.30.1`;
otherwise the shared support policy selects the smoke versions.

For an unsigned local build, use the extension's ordinary Bake targets with
`-f docker-bake.hcl -f docker-bake-pgrx.hcl -f <extension>/metadata.hcl`
in that order. Supply `build_timestamp` and the digest-qualified `sbom_generator`
from preparation. Select explicit named Bake targets to build a single local
distribution. Diagnostic `pgrx-sbom` output can
be used to inspect Cargo evidence; it does not test hosted signing.

## Dependency updates

Renovate manages PGRX source tags in extension metadata, build-tool versions in
`dependencies/tools.json` and `dependencies/workflow-tools.json`. Workflow execution
images remain digest-pinned in `workflow-tools.json`. CNPG support policy owns
its latest release pin in
`.github/workflows/cnpg-versions.yml`; operator manifests follow the same live
release-branch or `main` policy as shared smoke tests.

Preparation resolves the source revision and archive hash and selects each
platform child from the current Debian base tag. Base tags follow the shared
`getBaseImage` policy; their resolved digests are recorded per run rather than
maintained in a separate dependency manifest. Builds derive the matching cargo-pgrx
version from upstream Cargo.lock and tool artifact URLs from their managed
versions. No manual lock-refresh step is required. The resulting preparation
and build evidence record the source
identity, source hashes, tool versions, and actual platform base child. Review
source recipes and SQL version changes manually; `sql` remains independently
maintained in metadata and is not advanced by source tag updates.

The reporting-tool configuration owns the hook's embedded SPDX identifier list;
update that list when changing the license parser. System dependencies install
through the Debian apt repositories with the ordinary `apt-get update` and
`apt-get install` flow; individual package artifacts are not pinned in a
separate lock inventory.

The pinned toolbox image supplies the shared smoke-test environment. The shared
Taskfile owns the already pinned Kubernetes node and kubectl, and the shared
Dagger test function owns Chainsaw. PGRX overrides replace the mutable toolbox
installer with the pinned runner plus the version-selected Kind binary. Catalog
checks use the shared Task/Dagger tests without additional mounted-payload
assertions. Catalog installation follows the shared Taskfile unchanged: it installs Git with apk
and applies `cnpg-extensions/artifacts` catalogs from `main`.

PostgreSQL Anonymizer declares its GitLab `source_repository` in metadata and
uses the upstream `make extension` target, including runtime CSV
data. Payload evidence includes that data directory recursively. Its catalog
preloads `anon`; initialize its legacy fake-data functions with the mounted
data path described in the extension README.

Keep upstream recipe URL comments immediately above build commands. Add the
canonical `source_repository` and source tag to metadata for a new extension,
then add its recipe configuration and required apt dependencies, and extend the native matrix by metadata. Do not add a second SBOM
composer or a build-system-specific consumer interface.
