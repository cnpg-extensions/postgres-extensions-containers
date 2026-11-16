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
    build-essential ca-certificates curl git cmake ninja-build python3 pkg-config clang ccache \
    libssl-dev libcurl4-openssl-dev liblz4-dev libicu-dev postgresql-server-dev-${PG_MAJOR} \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
# Follow upstream's checkout procedure at the release selected by metadata.
RUN git clone --branch "${EXT_VERSION}" --single-branch https://github.com/duckdb/pg_duckdb . \
    && git submodule update --init --recursive

# Match upstream's Docker image compiler selection and default release build.
# Trixie supplies its supported Clang version rather than Bookworm's clang-14.
ENV DUCKDB_CC=/usr/bin/clang DUCKDB_CXX=/usr/bin/clang++
ENV PATH=/usr/lib/ccache:$PATH
ENV CCACHE_DIR=/ccache
RUN make clean-all \
    && make -j$(nproc) \
    && make install \
    && DESTDIR=/install make install

# Resolve Snappy's compiler-selected version for the SBOM hook.
RUN "${DUCKDB_CXX}" -dM -E -x c++ third_party/duckdb/third_party/snappy/snappy-stubs-public.h > /build/snappy-version.h

# Debian source-package copyright files, in the shared helper's layout.
COPY universe/pg-duckdb/licenses/ /licenses/
COPY universe/pg-duckdb/augment_spdx.py /usr/local/share/cnpg-sbom/augment_spdx.py
RUN mkdir -p /licenses/pg_duckdb \
    && cat /build/LICENSE /build/NOTICE > /licenses/pg_duckdb/copyright \
    && for package in libduckdb2.0 liblz4-1 libmbedcrypto16 libzstd1 libxxhash0; do \
         cp /usr/share/common-licenses/GPL-2 /licenses/$package/; done \
    && for package in libduckdb2.0 libmbedcrypto16 libyyjson0; do \
         cp /usr/share/common-licenses/Apache-2.0 /licenses/$package/; done

FROM scratch
ARG PG_MAJOR=18
COPY --from=builder /install/usr/lib/postgresql/${PG_MAJOR}/lib/pg_duckdb.so /lib/
COPY --from=builder /install/usr/share/postgresql/${PG_MAJOR}/extension/ /share/extension/
COPY --from=builder /install/usr/lib/postgresql/${PG_MAJOR}/lib/libduckdb.so /system/
COPY --from=builder /licenses/ /licenses/
USER 65532:65532
