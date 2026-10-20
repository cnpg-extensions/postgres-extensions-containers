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
`install-pgrx-build-environment.sh` installs exact apt artifacts, the locked Rust
distribution, the cargo-pgrx source matching the upstream Cargo lock, and pinned
reporting tools. It applies the existing JWT patch only to its declared release.
Cargo-about uses SHA-256-verified release binaries on both architectures, with
no source-build fallback. Only cargo-pgrx is built from its
locked source archive. All locked crate sources are fetched before offline
reporting because cargo-about queries metadata before applying its target filter.
No helper silently rewrites source versions or updates Cargo dependencies.

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

Preparation freezes the source snapshot, timestamp, generator, bases, targets,
and definitions for a logical workflow run. Every native platform job builds
one target on its matching architecture. It exports a complete OCI layout and a
record bound to that preparation. Assembly rejects missing or unexpected records,
validates their raw graphs, and uses full staging-index references in Buildx's
dry-run merge. Normal tags are assigned only after reading back a valid candidate.

Sign, security, smoke, and promotion consume per-target assembly artifacts.
Production promotion is restricted to trusted `main` push/dispatch events.
Grype reports vulnerabilities and Grant reports licenses; findings are retained for review,
while scanner errors fail the job. CNPG smoke installs pinned, published
CloudNativePG release manifests from the upstream `cloudnative-pg/cloudnative-pg`
repository and production `cloudnative-pg` operator images. CI exercises the locked production releases, currently 1.29 and 1.30.
The smoke uses pinned catalog fixtures and shared Task/Dagger tests, then checks
mounted-library hashes, ELF architecture, dynamic-library resolution, SQL version,
preload settings, and the pg-durable worker's connection to `app`. The shared finalizer additionally
stages Bookworm/amd64's required quadmath library and copyright for pg-search;
the existing OpenBLAS and Fortran copies remain in the recipe.

## Local validation

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
requires a trusted `main` event. An optional `cnpg_version` selects one locked
operator release; by default all supported locked releases are tested.

For an unsigned local build, use the extension's ordinary Bake targets with
`docker-bake-pgrx.hcl` and its `metadata.hcl`. Diagnostic `pgrx-sbom` output can
be used to inspect Cargo evidence; it does not test hosted signing.

## Dependency updates

All lock material lives in `dependencies/`. Renovate proposes source tags, tool
versions, image digests, and CNPG release tags/catalog commits. Operator fixtures
are fetched from the official versioned release manifests, not the unsupported
`artifacts` development snapshots. Coupled updates are not
automerged. Before merging, refresh the affected children and run the checks:

```sh
python3 pgrx/refresh_lock.py --refresh --only sources
python3 pgrx/refresh_lock.py --refresh --only tools
python3 pgrx/refresh_lock.py --refresh --only bases
python3 pgrx/refresh_lock.py --refresh --only fixtures
python3 pgrx/refresh_lock.py --check
```

Use only the refresh command relevant to the update. A source refresh binds the
tag, resolved commit, archive, upstream Cargo.lock, cargo-pgrx version, and CLI
crate checksum together. Review SQL version and upstream recipe changes manually.
Tool refreshes update both architectures and the full Rust distribution manifest.
The reporting-tool lock owns the hook's embedded SPDX identifier list; update that
list from cargo-about's locked `spdx` crate when upgrading its license parser.

Base-index updates own the platform-child and apt-artifact refresh. `refresh_apt.py`
uses native amd64 apt for both architectures; ARM package status is copied from
the pinned ARM base filesystem without executing ARM code. Signed apt indexes
supply dependency metadata and artifact hashes. Use `--distro bookworm` with
`refresh_apt.py` to refresh only Bookworm after an artifact expires.
The apt ownership record binds all four artifact lists to the base lock. Each
build verifies downloaded SHA256 values and disables repository fallback during
installation. An unavailable old artifact requires an explicit lock refresh.

The pinned toolbox image supplies the shared smoke-test environment. The shared
Taskfile owns the already pinned Kubernetes node and kubectl, and the shared
Dagger test function owns Chainsaw. PGRX overrides replace the mutable toolbox
installer with the pinned runner plus the checked Kind binary. No PGRX path
reinstalls unpinned apt/apk tools during smoke testing.

Keep upstream recipe URL comments immediately above build commands. Add a source
lock and recipe configuration for a new extension, refresh required system
artifacts, and extend the native matrix by metadata. Do not add a second SBOM
composer or a build-system-specific consumer interface.
