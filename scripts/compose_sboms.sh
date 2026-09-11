#!/usr/bin/env bash
set -Eeuo pipefail

# Export builder-stage SBOMs per target and selected platform; the pushed image
# supplies cached layers, and the final scratch stage is not scanned. Compose
# the platform documents into one SPDX payload per image target.
export environment=testing
export registry="${IMAGE_REGISTRY}"
export revision="${GITHUB_SHA}"
bake_file=docker-bake.hcl
distro=""
platforms=(linux/amd64 linux/arm64)
while (( $# )); do
  case "$1" in
    --bake-file)
      bake_file="${2:?missing value for --bake-file}"
      shift 2
      ;;
    --distro)
      distro="${2:?missing value for --distro}"
      shift 2
      ;;
    --platform)
      platforms=("${2:?missing value for --platform}")
      shift 2
      ;;
    *)
      echo "usage: $0 [--bake-file PATH] [--platform PLATFORM]" >&2
      exit 2
      ;;
  esac
done
export DISTRO="${distro}"
working_directory="${RUNNER_TEMP}/extension-sbom"
mkdir -p "${working_directory}/manifests" "${working_directory}/predicates" "${working_directory}/scans"
bake_files=(-f "${bake_file}" -f "${EXTENSION_NAME}/metadata.hcl")
bake_definition="${working_directory}/bake.json"
docker buildx bake "${bake_files[@]}" --print > "${bake_definition}"

# Inject the SBOM stage selector into a temporary Dockerfile.
sed '1iARG BUILDKIT_SBOM_SCAN_STAGE=builder' "${EXTENSION_NAME}/Dockerfile" > "${EXTENSION_NAME}/.sbom.Dockerfile"

mapfile -t bake_targets < <(jq -r '.target | keys[]' "${bake_definition}")
test "${#bake_targets[@]}" -gt 0
attestation_records=()
mapfile -t actions_attest_refs < <(
  sed -n 's/^[[:space:]]*uses:[[:space:]]*\(actions\/attest@[0-9a-f]\{40\}\).*/\1/p' \
    "${GITHUB_WORKSPACE}/.github/workflows/bake_targets.yml" | sort -u
)
test "${#actions_attest_refs[@]}" -eq 1
actions_attest_ref="${actions_attest_refs[0]}"

for bake_target in "${bake_targets[@]}"; do
  image=$(jq -r --arg target "${bake_target}" '.target[$target].tags[0]' "${bake_definition}")
  test -n "${image}" && test "${image}" != "null"

  builder_sbom_records=()
  builder_sbom_paths=()
  scancode_report_paths=()
  platform_manifest_records=()
  for platform in "${platforms[@]}"; do
    output_directory="${working_directory}/${bake_target}-${platform//\//-}"
    mkdir -p "${output_directory}"

    # BuildKit reuses the pushed build's cached layers; this adds only the
    # local SBOM generation and export work.
    docker buildx bake "${bake_files[@]}" "${bake_target}" \
      --set "*.platform=${platform}" \
      --set "*.dockerfile=.sbom.Dockerfile" \
      --set "*.output=type=local,dest=${output_directory}" \
      --set "*.attest=type=sbom" \
      --progress plain

    builder_sbom="${output_directory}/sbom-builder.spdx.json"
    jq -e '.predicateType == "https://spdx.dev/Document" and .predicate.name == "sbom-builder" and (.subject | length > 0)' "${builder_sbom}"
    scancode_report="${working_directory}/scans/${bake_target}-${platform//\//-}.json"
    license_scan_root="${working_directory}/license-chunks/${bake_target}-${platform//\//-}/licenses"
    find "${output_directory}/licenses" -type f -print0 | while IFS= read -r -d '' license_file; do
      chunk_directory="${license_scan_root}/${license_file#${output_directory}/licenses/}"
      mkdir -p "${chunk_directory}"
      csplit -s -z -f "${chunk_directory}/license-" "${license_file}" '/^License:/' '{*}' >/dev/null
    done
    scancode --license --license-references --json "${scancode_report}.chunks" "${license_scan_root}"
    jq '.files[] |= if .type == "file" then (.path |= sub("/license-[0-9]+$"; "") | (.license_detections[]?.matches[]?.from_file) |= sub("/license-[0-9]+$"; "")) else . end' "${scancode_report}.chunks" > "${scancode_report}" && rm "${scancode_report}.chunks"

    image_manifest_file="${output_directory}/image-manifest.json"
    docker buildx imagetools inspect "${image}" --raw > "${image_manifest_file}"
    if jq -e '(.manifests? | type) == "array"' "${image_manifest_file}" > /dev/null; then
      image_manifest_digest=$(jq -r --arg architecture "${platform#*/}" '
        [.manifests[] |
         select(.platform.os == "linux" and .platform.architecture == $architecture) |
         .digest] | first // empty' "${image_manifest_file}")
    else
      image_manifest_digest=$(sha256sum "${image_manifest_file}" | awk '{print "sha256:" $1}')
    fi
    test -n "${image_manifest_digest}" && test "${image_manifest_digest}" != "null"

    builder_sbom_paths+=("${builder_sbom}")
    scancode_report_paths+=("${scancode_report}")
    builder_sbom_records+=("{\"platform\":\"${platform}\",\"sha256\":\"$(sha256sum "${builder_sbom}" | awk '{print $1}')\"}")
    platform_manifest_records+=("{\"platform\":\"${platform}\",\"manifestDigest\":\"${image_manifest_digest}\"}")
  done

  # The raw index bytes are the subject digest for the aggregate attestation.
  # This intentionally excludes the final SPDX hash; the signed attestation
  # and OCI descriptor bind that content.
  image_index_digest=$(docker buildx imagetools inspect "${image}" --raw | \
    sha256sum | awk '{print "sha256:" $1}')

  provenance_manifest="${working_directory}/manifests/${bake_target}.json"
  predicate="${working_directory}/predicates/${bake_target}/extension-sbom.spdx.json"
  mkdir -p "${predicate%/*}"
  compose_args=(
    ./scripts/compose_sbom.py
    --extension-name "${EXTENSION_NAME}"
    --output "${predicate}"
  )
  for index in "${!platforms[@]}"; do
    compose_args+=(
      --builder-sbom "${builder_sbom_paths[$index]}"
      --scancode-report "${scancode_report_paths[$index]}"
      --platform "${platforms[$index]}"
    )
  done
  cat > "${provenance_manifest}" <<EOF
{
  "schemaVersion": "https://github.com/cnpg-extensions/postgres-extensions-containers/sbom-composition/v1",
  "annotationDate": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "inputs": {
    "builderSboms": [$(IFS=,; printf '%s' "${builder_sbom_records[*]}")],
    "buildDefinition": {"sha256": "$(sha256sum "${bake_definition}" | awk '{print $1}')"}
  },
  "image": {
    "sourceCommit": "${GITHUB_SHA}",
    "target": "${bake_target}",
    "platforms": [$(IFS=,; printf '%s' "${platform_manifest_records[*]}")],
    "indexDigest": "${image_index_digest}"
  },
  "composer": {
    "revision": "$(git rev-parse HEAD)",
    "command": "$(printf '%q ' "${compose_args[@]}")",
    "interpreter": "$(python3 --version 2>&1)",
    "toolVersions": {
      "docker": "$(docker --version)",
      "buildx": "$(docker buildx version)",
      "jq": "$(jq --version)",
      "scancode": "$(scancode --version | head -n 1)",
      "actionsAttest": "${actions_attest_ref}"
    }
  },
  "workflow": {
    "repository": "${GITHUB_REPOSITORY}",
    "name": "${GITHUB_WORKFLOW}",
    "ref": "${GITHUB_REF}",
    "runId": "${GITHUB_RUN_ID}",
    "runAttempt": "${GITHUB_RUN_ATTEMPT}",
    "actor": "${GITHUB_ACTOR}"
  }
}
EOF
  jq -e --arg namespace "https://github.com/cnpg-extensions/postgres-extensions-containers/sbom-composition/v1" \
    --argjson platform_count "${#platforms[@]}" \
    --arg index_digest "${image_index_digest}" \
    --arg actions_attest_ref "${actions_attest_ref}" \
    '.schemaVersion == $namespace and
     (.inputs.builderSboms | length == $platform_count) and
     (.image.platforms | length == $platform_count) and
     .image.indexDigest == $index_digest and
     .composer.toolVersions.actionsAttest == $actions_attest_ref' \
    "${provenance_manifest}"

  "${compose_args[@]}"

  jq -e \
    --arg namespace "https://github.com/cnpg-extensions/postgres-extensions-containers/sbom-composition/v1" \
    --arg annotation_date "$(jq -r '.annotationDate' "${provenance_manifest}")" \
    --arg provenance "$(jq -cS . "${provenance_manifest}")" \
    --arg document_namespace "https://github.com/cnpg-extensions/postgres-extensions-containers/sbom-composition/v1/documents/${EXTENSION_NAME}/${image_index_digest//:/-}" \
    '.documentNamespace = $document_namespace |
     .annotations = ((.annotations // []) + [{
       annotationDate: $annotation_date,
       annotationType: "OTHER",
       annotator: "Tool: bake_targets.yml",
       comment: ($namespace + " " + $provenance),
       spdxElementId: "SPDXRef-DOCUMENT"
     }])' \
    "${predicate}" > "${predicate}.tmp"
  mv "${predicate}.tmp" "${predicate}"

  attestation_records+=("{\"target\":\"${bake_target}\",\"testingImage\":\"${image}\",\"testingSubject\":\"${image%:*}\",\"productionImage\":\"${image/-testing:/:}\",\"productionSubject\":\"${image%%-testing:*}\",\"indexDigest\":\"${image_index_digest}\",\"predicatePath\":\"predicates/${bake_target}/extension-sbom.spdx.json\"}")
done

cat > "${working_directory}/attestation-manifest.json" <<EOF
[$(IFS=,; printf '%s' "${attestation_records[*]}")]
EOF
manifest=$(jq -c . "${working_directory}/attestation-manifest.json")
echo "manifest=${manifest}" >> "$GITHUB_OUTPUT"
