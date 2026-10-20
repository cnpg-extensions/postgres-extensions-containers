# Verify and scan an extension image

Use the same procedure for every extension image. It verifies a signed OCI index,
selects a platform, checks its complete attestation graph, and extracts SPDX and
provenance only after validation succeeds. No build-system option is required.

Install the locked tools from this checkout:

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

python3 pgrx/verify.py --image "$IMAGE" --platform "$PLATFORM" \
  --certificate-identity-regexp "$POLICY" \
  --certificate-oidc-issuer "$ISSUER" \
  --output-directory ./verified-amd64

grype sbom:./verified-amd64/sbom.spdx.json | grep -E 'NAME|High|Critical' | grep -v "won't fix"
grant list ./verified-amd64/sbom.spdx.json 2>/dev/null | ansi2txt
```

Replace the owner in both the image and the anchored identity policy if you
trust another publisher. Keep the workflow filenames, branch, issuer, and
repository explicit. Do not accept a broad owner or repository wildcard.
Current and legacy Cosign signature formats use the same trust checks.
The output directory must not exist; use a fresh directory for each image and
platform. Repeat with `linux/arm64` and a separate directory for an ARM child.

`verification.json` records the index, platform, and Cosign verification result.
`provenance.json` contains the matching platform's BuildKit provenance.
`sbom.spdx.json` is the matching SPDX predicate. The verifier reads the raw OCI
blobs, checks descriptor sizes and SHA256 hashes, matches runnable platform
configurations, verifies both OCI and in-toto subjects, and compares ordinary
Buildx extraction with the validated predicates. Missing, duplicate, corrupt,
ambiguous, or wrong-platform evidence fails without publishing output.

BuildKit places SPDX and provenance inside the signed index. `cosign verify`
authenticates that index; `cosign verify-attestation` is not the retrieval path
for these embedded BuildKit attestations. Buildx extraction alone does not
check the publisher signature or the complete graph. Buildx returns an SPDX
stub for a single-platform index and a platform map for a multi-platform index;
the verifier handles both shapes identically for all extensions.

Grype and Grant scan the extracted document; they do not authenticate it. Reports cover
the shipped extension payload and its selected dependencies, not the PostgreSQL
base image or other extension volumes. Scan those images separately. PGRX Cargo
relationships describe the configured target dependency graph; they do not
claim that every dependency survives linker dead-code elimination.

After copying an image, run the same verification against the destination
repository and its signature. A successful source verification does not
authenticate a separate repository. The hosted promotion workflow preserves
digests, signs the copied index, and verifies both platforms again.
