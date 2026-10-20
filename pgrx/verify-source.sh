#!/usr/bin/env bash
# Verify before extraction or execution of upstream source/patches.
set -Eeuo pipefail
[[ ${PGRX_SOURCE_SHA256:-} =~ ^[a-f0-9]{64}$ ]] || { echo 'missing source archive pin' >&2; exit 1; }
printf '%s  /tmp/source.tar.gz\n' "$PGRX_SOURCE_SHA256" | sha256sum --check --strict -
