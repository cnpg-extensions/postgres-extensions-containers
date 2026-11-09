# Verify and scan an extension image

Use standard Cosign and Buildx commands for every extension image. Install the
locked workflow tools from this checkout, plus Docker with Buildx and jq:

```sh
python3 pgrx/bootstrap_workflow_tools.py --output /tmp/extension-tools
export PATH=/tmp/extension-tools:$PATH
```

Choose an immutable index digest, a platform, and the publisher you trust. For
production images from this repository's `main` branch:

```sh
IMAGE='ghcr.io/cnpg-extensions/EXTENSION@sha256:INDEX_DIGEST'
PLATFORM='linux/amd64'
POLICY='^https://github\.com/cnpg-extensions/postgres-extensions-containers/\.github/workflows/(bake_targets|pgrx_targets)\.yml@refs/heads/main$'
ISSUER='https://token.actions.githubusercontent.com'

cosign verify --new-bundle-format=false \
  --certificate-identity-regexp "$POLICY" \
  --certificate-oidc-issuer "$ISSUER" "$IMAGE"
```

Continue only after signature verification succeeds. Replace the owner in both
the image and the anchored identity policy if you trust another publisher. Keep
the workflow filenames, branch, issuer, and repository explicit. Do not accept a
broad owner or repository wildcard. The command selects the legacy signature
format used by this repository's signing jobs. For signatures published in the
new bundle format, use `--new-bundle-format=true` with the same identity and issuer.

Extract the selected platform's SPDX document and embedded BuildKit provenance
from the same digest-qualified image:

```sh
mkdir -p evidence-amd64

docker buildx imagetools inspect "$IMAGE" --format '{{json .SBOM}}' \
  | jq -e --arg platform "$PLATFORM" '(.[$platform] // .).SPDX // error("missing platform SPDX")' \
  > evidence-amd64/sbom.spdx.json

docker buildx imagetools inspect "$IMAGE" --format '{{json .Provenance}}' \
  | jq -e --arg platform "$PLATFORM" '(.[$platform] // .).SLSA // error("missing platform provenance")' \
  > evidence-amd64/provenance.json

grype sbom:./evidence-amd64/sbom.spdx.json | grep -E 'NAME|High|Critical' | grep -v "won't fix"
grant list ./evidence-amd64/sbom.spdx.json 2>/dev/null | ansi2txt
```

Buildx returns a single-platform stub with `SPDX` or `SLSA` directly on the object,
and a platform-keyed map for multi-platform indexes. The jq expressions handle
both shapes. For a single-platform index, confirm that its platform matches
`PLATFORM` in `docker buildx imagetools inspect "$IMAGE"` before extraction.
Repeat with `linux/arm64` and a separate output directory for an ARM child.

BuildKit embeds these attestations in the signed index. `cosign verify`
authenticates that index; `cosign verify-attestation` is not the retrieval path
for embedded BuildKit attestations. These commands rely on standard tool
verification and extraction; they do not perform exhaustive custom OCI graph
checks or compare provenance fields against preparation records.

Hosted workflows also publish independent SLSA attestations for testing and
production indexes using the shared reusable SLSA generator. This procedure does
not verify those separate workflow SLSA attestations.

Grype and Grant scan the extracted document; they do not authenticate it. Reports
cover the shipped extension payload and its selected dependencies, not the
PostgreSQL base image or other extension volumes. Scan those images separately.
PGRX Cargo relationships describe the configured target dependency graph; they
do not claim that every dependency survives linker dead-code elimination.

After copying an image, run the same verification against the destination
repository and its signature. A successful source verification does not
authenticate a separate repository. Hosted promotion uses CloudNativePG's shared
`copy-images` action to copy all platforms and sign the production digests,
followed by production SLSA provenance. It does not repeat this consumer procedure.
