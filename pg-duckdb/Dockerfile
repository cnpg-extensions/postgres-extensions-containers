# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

# Capture base image libraries before installing any packages.
COPY scripts/capture_base_image_libs.sh /usr/local/bin/capture_base_image_libs.sh
RUN /usr/local/bin/capture_base_image_libs.sh

# pg_duckdb is not packaged by PGDG or Debian, so it is built from the upstream
# release tag (MIT). DuckDB is a git submodule pinned by that tag.
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential ca-certificates cmake git libcurl4-openssl-dev libicu-dev liblz4-dev \
      libssl-dev ninja-build pkg-config "postgresql-server-dev-${PG_MAJOR}"

WORKDIR /src
RUN git clone --depth 1 --branch "v${EXT_VERSION}" \
      --recurse-submodules --shallow-submodules \
      https://github.com/duckdb/pg_duckdb.git .

# DUCKDB_BUILD=ReleaseStatic links DuckDB into pg_duckdb.so, so no libduckdb.so
# has to be shipped. with_llvm=no skips bitcode, which needs clang.
RUN make -j"$(nproc)" DUCKDB_BUILD=ReleaseStatic with_llvm=no && \
    make install DUCKDB_BUILD=ReleaseStatic with_llvm=no

RUN mkdir -p /licenses/pg-duckdb /licenses/duckdb && \
    cp LICENSE /licenses/pg-duckdb/ && \
    cp third_party/duckdb/LICENSE /licenses/duckdb/

# Gather system libraries and their licenses
COPY scripts/stage_system_libs.sh /usr/local/bin/stage_system_libs.sh
RUN /usr/local/bin/stage_system_libs.sh "/usr/lib/postgresql/${PG_MAJOR}/lib/pg_duckdb.so"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /licenses /licenses/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_duckdb.so /lib/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_duckdb* /share/extension/

# System libs
COPY --from=builder /system /system/

USER 65532:65532
