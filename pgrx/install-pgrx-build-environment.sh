#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
set -Eeuo pipefail
pg_major=${1:?PostgreSQL major version is required}
lock_file=${2:?full path to Cargo.lock is required}
[[ "$lock_file" == /build/Cargo.lock ]]
: "${PGRX_EXTENSION:?}" "${PGRX_DISTRO:?}" "${TARGETARCH:?}"
# Resolve build dependencies through the distribution repositories, as the
# Debian extension builders do. Runtime libraries are staged separately.
apt-get update
apt-get install --yes --no-install-recommends \
    build-essential \
    ca-certificates \
    clang \
    cmake \
    curl \
    git \
    jq \
    libclang-dev \
    libicu-dev \
    libssl-dev \
    pkg-config \
    python3 \
    "postgresql-server-dev-${pg_major}" \
    xz-utils \
    patch
rm -rf /var/lib/apt/lists/*
python3 /pgrx/install_tools.py "$pg_major" "$lock_file"
install -D -m 0644 /pgrx/sbom/augment_spdx.py /usr/local/share/cnpg-sbom/augment_spdx.py
