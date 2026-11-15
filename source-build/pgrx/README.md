# PGRX recipe development

PGRX recipes are discovered from `pgrx/<extension>/metadata.hcl`. Directory location selects the PGRX build family.

**Start from the [PGRX templates](templates/) and follow their structure.**
The [Dockerfile template](templates/Dockerfile.tmpl) contains the integration
points used by CI, native builds, and SBOM generation. Adapt the source URL,
upstream build commands, dependencies, and copied runtime files for the extension;
keep the shared setup and evidence steps.

For a new extension:

1. Copy and complete the Dockerfile, metadata, and README templates, replacing
   every placeholder and TODO. Set the canonical source repository in the
   Dockerfile and the literal source tag in metadata, including a leading `v`
   when upstream uses one.
   Set `sql` to the tag without a leading `v`, immediately below `package` so
   Renovate updates both together.
2. Preserve all Dockerfile `ARG` declarations **in their template locations and
   stages**, including `BUILDKIT_SBOM_SCAN_STAGE`, `BASE`, `PG_MAJOR`, `EXT_VERSION`,
   `TARGETARCH`, `TARGETPLATFORM`, `PGRX_EXTENSION`, `PGRX_DISTRO`, and
   `PGRX_BUILD_TIMESTAMP`. They pass CI's selected versions, architecture, source
   selection, and timestamp into the build and evidence tools. Some are consumed
   by helper scripts rather than referenced directly in the Dockerfile. Docker
   arguments are stage-scoped, so retain repeated declarations such as `PG_MAJOR`
   in the final stage too.
3. Keep the stage named `builder`, copy `source-build/` to `/source-build/`, and extract the source
   into `/build`. **Call `/source-build/pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}"
   /build/Cargo.lock` after extraction and before compilation.** It installs the
   build environment, selects cargo-pgrx from the source lockfile, and prepares
   the SBOM hook and reporting tools.
4. Add the extension to `RECIPES` in [`build_config.py`](build_config.py), matching
   the Dockerfile's manifest path, features, and package/install layout. Add any
   required apt dependencies and keep the upstream recipe URL immediately above
   the build commands.
5. **Call `/source-build/pgrx/finalize-pgrx-evidence.sh` after compilation and packaging.** It
   records the completed payload and generates Cargo and license evidence needed
   by the SBOM hook. Preserve the diagnostic `pgrx-sbom` stage and copy the
   generated Rust license notices into the final image alongside the runtime
   files, as the template shows.
6. Declare supported distribution/PostgreSQL combinations in metadata;
   preparation creates their native build jobs automatically. Run the shared
   [local builds and checks](../README.md#local-builds). Use the existing SBOM generator
   and hook; do not add a second composer or a build-system-specific consumer
   interface.

In the extension README, explain SQL and catalog names, preload requirements,
and any initialization steps.

### Recipes with additional runtime needs

Recipes that need additional OS runtime libraries capture base libraries before
installing packages, then stage the packaged extension's additional runtime
closure and copyright notices using the shared helpers. pg-search 0.26.6 uses
LLD and OpenBLAS at build time but does not stage additional runtime libraries.

PostgreSQL Anonymizer declares its GitLab source URL in its Dockerfile and
uses the upstream `make extension` target, including runtime CSV data. Payload
evidence includes that data directory recursively. Its catalog preloads `anon`;
initialize its legacy fake-data functions with the mounted data path described
in the extension README.

### PGRX source updates

Renovate PGRX source and build-tool updates inherit the shared minor, patch and
digest automerge policy, subject to required checks. Major updates remain manual.
Renovate updates `package` and the adjacent `sql` value together for every PGRX
extension, stripping only a leading `v` from the source tag for SQL. If upstream
ships a different SQL version, investigate the release before merging.

## PGRX Bake targets

Use the extension's ordinary Bake targets with
`-f docker-bake.hcl -f docker-bake-pgrx.hcl -f pgrx/<extension>/metadata.hcl`
in that order. Supply `build_timestamp` and the digest-qualified `sbom_generator`
from preparation. Select explicit named Bake targets to build a single local
distribution, and restrict the platform to your host's native architecture
(for example, `--set '*.platforms=linux/amd64'` on AMD64). Do not emulate the
other architecture for a Rust build.

The diagnostic `pgrx-sbom` target exports Cargo evidence for inspection. It does
not replace an image build that produces attestations or test hosted signing.

## Tools

Extension-specific Dockerfiles and metadata live under `pgrx/<extension>/`. Rust-specific
tools live under `source-build/pgrx/`:

| File or directory | Purpose |
| --- | --- |
| [`build_config.py`](build_config.py) | Registers extension recipes and their Cargo feature selection. |
| [`install-pgrx-build-environment.sh`](install-pgrx-build-environment.sh) | Required Dockerfile setup step: installs build tools and the SBOM hook. |
| [`finalize-pgrx-evidence.sh`](finalize-pgrx-evidence.sh) | Required post-build step: collects Cargo, license, and runtime-payload evidence. |
| [`templates/`](templates/) | Dockerfile, metadata, and README templates to follow for new extensions. |
| [`sbom/`](sbom/) | Hook that adds verified Rust dependencies and licenses to the shared generator's SPDX output. |
| [`dependencies/`](dependencies/) | Rust, rustup, and cargo-about version configuration for extension builders. |
| [`tests/`](tests/) | PGRX tests, run with `python3 source-build/test.py`. |

See the [shared source-build guide](../README.md) for dependency evidence,
local builds, tooling tests and image verification.
