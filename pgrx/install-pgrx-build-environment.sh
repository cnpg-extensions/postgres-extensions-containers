#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
set -Eeuo pipefail
pg_major=${1:?PostgreSQL major version is required}
lock_file=${2:?full path to Cargo.lock is required}
[[ "$lock_file" == /build/Cargo.lock ]]
: "${PGRX_EXTENSION:?}" "${PGRX_DISTRO:?}" "${TARGETARCH:?}"
package_lock="/pgrx/dependencies/apt/${PGRX_DISTRO}-${TARGETARCH}.tsv"
test -s "$package_lock"
mkdir -p /tmp/pgrx-debs
while IFS=$'\t' read -r checksum filename url; do
    [[ "$checksum" =~ ^[a-f0-9]{64}$ && "$filename" != */* ]]
    /usr/lib/apt/apt-helper download-file "$url" "/tmp/pgrx-debs/$filename" "SHA256:$checksum"
    printf '%s  %s\n' "$checksum" "/tmp/pgrx-debs/$filename" | sha256sum --check --strict -
done < "$package_lock"
# Empty sources/lists permit local .deb acquisition while making repository
# fallback impossible. --no-download also disables apt's local file acquisition.
mkdir -p /tmp/pgrx-empty-apt-lists
apt-get --yes --no-install-recommends \
    -o Dir::Etc::sourcelist=/dev/null -o Dir::Etc::sourceparts=- \
    -o Dir::State::lists=/tmp/pgrx-empty-apt-lists \
    install /tmp/pgrx-debs/*.deb
rm -rf /tmp/pgrx-debs /var/lib/apt/lists/*
python3 /pgrx/install_tools.py "$pg_major" "$lock_file"
install -D -m 0644 /pgrx/sbom/augment_spdx.py /usr/local/share/cnpg-sbom/augment_spdx.py
