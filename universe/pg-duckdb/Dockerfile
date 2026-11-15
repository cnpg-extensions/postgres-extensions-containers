# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0

# BuildKit scans the builder, including recipe-owned source evidence.
ARG BUILDKIT_SBOM_SCAN_STAGE=builder
ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM ${BASE} AS builder

ARG PG_MAJOR=18
ARG EXT_VERSION
ARG TARGETARCH

USER 0
COPY source-build/ /source-build/

# Build tools and system development libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates curl jq git cmake ninja-build python3 pkg-config \
    libssl-dev libcurl4-openssl-dev liblz4-dev libicu-dev postgresql-server-dev-${PG_MAJOR} \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
# Resolve the release once so all three archives use matching source revisions.
RUN set -eu; \
    curl -fsSL "https://api.github.com/repos/duckdb/pg_duckdb/commits/${EXT_VERSION}" -o /tmp/release.json; \
    revision=$(jq -er '.sha | select(test("^[0-9a-f]{40}$"))' /tmp/release.json); \
    curl -fsSL "https://github.com/duckdb/pg_duckdb/archive/${revision}.tar.gz" -o /tmp/pg_duckdb.tar.gz; \
    tar -xzf /tmp/pg_duckdb.tar.gz --strip-components=1 --no-same-owner -C /build; \
    curl -fsSL "https://api.github.com/repos/duckdb/pg_duckdb/git/trees/${revision}?recursive=1" -o /tmp/tree.json; \
    duckdb_revision=$(jq -er '.tree[] | select(.path == "third_party/duckdb" and .type == "commit") | .sha | select(test("^[0-9a-f]{40}$"))' /tmp/tree.json); \
    mkdir -p third_party/duckdb third_party/httpfs; \
    curl -fsSL "https://github.com/duckdb/duckdb/archive/${duckdb_revision}.tar.gz" -o /tmp/duckdb.tar.gz; \
    tar -xzf /tmp/duckdb.tar.gz --strip-components=1 --no-same-owner -C third_party/duckdb; \
    httpfs_revision=$(sed -n 's/^[[:space:]]*GIT_TAG \([0-9a-f]\{40\}\)[[:space:]]*$/\1/p' third_party/pg_duckdb_extensions.cmake); \
    test "${#httpfs_revision}" -eq 40; \
    curl -fsSL "https://github.com/duckdb/duckdb-httpfs/archive/${httpfs_revision}.tar.gz" -o /tmp/httpfs.tar.gz; \
    tar -xzf /tmp/httpfs.tar.gz --strip-components=1 --no-same-owner -C third_party/httpfs; \
    # Use the downloaded httpfs archive instead of CMake's Git acquisition. \
    sed -i "s|GIT_URL https://github.com/duckdb/duckdb-httpfs|SOURCE_DIR /build/third_party/httpfs|; s|GIT_TAG ${httpfs_revision}|EXTENSION_VERSION ${httpfs_revision}|" third_party/pg_duckdb_extensions.cmake; \
    # Upstream Make requires this gitlink marker even when using source archives. \
    mkdir -p .git/modules/third_party/duckdb; \
    printf '%s\n' "$duckdb_revision" > .git/modules/third_party/duckdb/HEAD; \
    jq -n --arg revision "$revision" --arg duckdb_revision "$duckdb_revision" \
        --arg httpfs_revision "$httpfs_revision" --arg version "$EXT_VERSION" \
        '{repository: "https://github.com/duckdb/pg_duckdb", revision: $revision, duckdb_revision: $duckdb_revision, httpfs_revision: $httpfs_revision, version: $version}' \
        > source-evidence.json; \
    rm /tmp/release.json /tmp/tree.json /tmp/pg_duckdb.tar.gz /tmp/duckdb.tar.gz /tmp/httpfs.tar.gz

# Upstream recipe: https://github.com/duckdb/pg_duckdb/blob/v1.2.0/docs/compilation.md
RUN CMAKE_BUILD_PARALLEL_LEVEL=2 make -j2 DISABLE_UNITY=1 DUCKDB_BUILD=ReleaseStaticSystem PG_CONFIG=/usr/lib/postgresql/${PG_MAJOR}/bin/pg_config PG_DUCKDB_VERSION=${EXT_VERSION} \
    && CMAKE_BUILD_PARALLEL_LEVEL=2 make -j2 DISABLE_UNITY=1 install DESTDIR=/install DUCKDB_BUILD=ReleaseStaticSystem PG_CONFIG=/usr/lib/postgresql/${PG_MAJOR}/bin/pg_config

# Stage the payload and original notices; add recipe-owned SBOM evidence.
ARG BUILD_TIMESTAMP
COPY universe/pg-duckdb/evidence.py universe/pg-duckdb/augment_spdx.py /recipe/
RUN python3 /recipe/evidence.py \
    && install -D -m 0644 /recipe/augment_spdx.py /usr/local/share/cnpg-sbom/augment_spdx.py

FROM scratch
COPY --from=builder /payload/ /
USER 65532:65532
