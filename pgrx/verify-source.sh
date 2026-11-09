#!/usr/bin/env bash
# Workflows freeze a source checksum for all native jobs in a run. Local builds
# use the metadata version directly and record the fetched source during setup.
set -Eeuo pipefail
if [[ -n ${PGRX_SOURCE_SHA256:-} ]]; then
    [[ $PGRX_SOURCE_SHA256 =~ ^[a-f0-9]{64}$ ]] || { echo 'invalid prepared source checksum' >&2; exit 1; }
    printf '%s  /tmp/source.tar.gz\n' "$PGRX_SOURCE_SHA256" | sha256sum --check --strict -
fi
