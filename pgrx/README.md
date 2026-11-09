# PGRX extension builds

PGRX targets are discovered from `build_system = "pgrx"` in ordinary extension
metadata. `get-targets` defaults to Debian; use `--build-system pgrx` for PGRX
or `--build-system all` for both families. OS-library maintenance excludes PGRX
targets; catalog and testing-value generation support both. Source tags remain literal
(including `v`), while SQL versions remain separate. Extension READMEs describe
usage; this directory contains build and validation internals.

## Verify images

Follow the SBOM guide to [verify the image and extract its
SBOM](../sbom-generator/README.md#verify-the-image-and-extract-its-sbom),
[inspect and verify build provenance](../sbom-generator/README.md#inspect-and-verify-build-provenance),
and [report vulnerabilities and licenses](../sbom-generator/README.md#report-vulnerabilities-and-licenses).
Use the tools listed there; installing the PGRX workflow toolchain is unnecessary.

For PGRX images published by `cnpg-extensions` from `main`, use this exact
`--certificate-identity` in the guide's Cosign command:

```text
https://github.com/cnpg-extensions/postgres-extensions-containers/.github/workflows/pgrx_targets.yml@refs/heads/main
```

Keep the guide's GitHub Actions OIDC issuer and add
`--new-bundle-format=false` for this repository's legacy-format signatures.
For another publisher, change both the image repository and the exact workflow
identity to that publisher's repository and trusted branch. After copying an
image, verify the destination repository's signature as well.

The guide's extraction examples use a multi-platform index. For a
single-platform index, confirm its platform with `docker buildx imagetools
inspect`, then use `.SBOM.SPDX` and `.Provenance.SLSA` in the format expressions.

PGRX Cargo relationships describe the configured target dependency graph; they
do not claim that every dependency survives linker dead-code elimination.

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
`patches` evidence field remains empty for schema compatibility. Pglinter 2.0.0
omits Cargo.lock, so its Dockerfile downloads the first upstream lockfile from
a pinned commit with a checksum. Version, manifest, and absence guards require
manual review on the next release; see the [workaround register](../WORKAROUNDS.md#pglinter-200-missing-cargolock).
Both lock hashes describe that borrowed file, not a lockfile in the release archive.
Cargo-about and other release tools use architecture-specific artifacts resolved from their
Renovate-managed versions. Only cargo-pgrx is built from source. All locked crate
sources are fetched before offline reporting because cargo-about queries
metadata before applying its target filter.
Preparation resolves each metadata source tag to a repository revision and
archive URL. Each native build downloads the archive from the upstream HTTPS
source and records its hash in build evidence, without comparing it against a
prepared checksum.
The build records the upstream Cargo.lock hash and derives cargo-pgrx from that
lock; these generated inputs are not maintained in a separate committed lock.

The post-build finalizer resolves target-filtered Cargo metadata using the same
package, PostgreSQL feature, non-PG defaults, and feature policy as cargo-pgrx.
Pglinter follows upstream's `release-lto-off` profile on ARM64 and `release`
on AMD64; build evidence records the selected profile and reads its package directory.
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
full SPDX validation after the hook returns.
cargo-about 0.9.2's repeated,
identical Boolean `doctest` field is normalized before report hashing. Other
duplicate JSON keys and conflicting values are rejected.

Preparation freezes the workspace snapshot, timestamp, generator, resolved source
identities, base indexes, targets, and definitions for a logical
workflow run. Each base index resolves to its architecture-specific child
manifest. Every native platform job builds one target on its matching
architecture and records its staging-index digest, bound to that preparation.
Assembly rejects missing or unexpected records and merges the full staging
indexes. Before assigning normal tags, it checks that the candidate preserves
the source descriptors and includes every expected architecture and its attached
attestation.

Sign, security, and smoke consume per-target assembly artifacts. Promotion passes
the combined Bake metadata to the same CloudNativePG `copy-images` action used
by Debian builds; that action copies the images and signs production digests.
The shared reusable SLSA generator attests each assembled testing index; its
success gates promotion. After promotion, the same generator attests each index
in its production repository. Production promotion is restricted to trusted
`main` push/dispatch events.
Grype reports vulnerabilities and Grant reports licenses; findings are retained for review,
while scanner errors fail the job. Both build paths use the shared CNPG support
policy: `main`, the highest stable patch of the previous minor, and the pinned
latest release. Smoke uses the shared Taskfile's live operator manifests and
catalogs, including development images for `main`.

[`cnpg-versions.yml`](../.github/workflows/cnpg-versions.yml) holds this policy
so Debian and PGRX test the same supported operator versions, with one
Renovate-managed latest-release pin. The logic was extracted from Debian's
`bake_targets.yml` to avoid maintaining a separate PGRX support matrix.
This adds a small difference from upstream's inline workflow: when upstream
changes that version-selection logic, apply its intent to the shared workflow,
even if Git merges cleanly. See the [upstream merge process](../MERGE.md).

PGRX follows the Debian release-acceptance level: build-time validation, security
scanning, signing, shared runtime smoke tests, and required SLSA jobs. Security
extracts each platform's SPDX document with Buildx for Grype and Grant.
These stages do not repeat full OCI-graph verification or compare every BuildKit
provenance field against preparation records. Consumers can [verify images](#verify-images)
using the shared SBOM guide and the PGRX signing identity above.
The smoke uses the shared Task/Dagger setup, CNPG extension catalogs, and
extension installation checks. The pg-search recipe
captures base libraries before installing packages, then stages the packaged
extension's additional runtime closure and copyright notices using the shared
helpers. This includes quadmath where required.

## Local validation

The dedicated PGRX contract workflow runs independently of Go tests. It does not
replace the shared Automerge gate or change branch protection.

Run from the repository root with actionlint and Python available. The Python
tests also run Syft against fixture lockfiles and require the SPDX validator.
Docker is needed for the tool extraction below.
Signing and full extension acceptance run in GitHub Actions
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

Run the PGRX tests and relevant workflow lint:

```sh
python3 pgrx/test.py && \
  actionlint .github/workflows/pgrx.yml \
    .github/workflows/pgrx_targets.yml \
    .github/workflows/pgrx-tests.yml \
    .github/workflows/cnpg-versions.yml
```

Shared Go and SBOM-generator suites have their own workflows. Run them separately
when changing shared code or an integration boundary. PGRX tests retain coverage
for Rust package selection, licenses, ownership, shipped files, generator/hook
composition, build selection, and native-platform assembly.
SBOM tests focus on mistakes that can produce a successful build with an
incorrect inventory, ownership, dependency graph, or license report. Malformed
evidence and other inputs that already cause a clear build failure rely on the
build-time guards rather than separate rejection tests.

For a quick downstream-only check, use `python3 pgrx/test.py`. CI runs this suite
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

Preparation resolves the source revision and archive URL and selects each
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
