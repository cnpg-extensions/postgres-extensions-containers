# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

# pg_parquet is not packaged by PGDG or Debian, so it is built from the upstream
# release tag (PostgreSQL License) with pgrx.
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential ca-certificates clang cmake curl git libclang-dev \
      libssl-dev pkg-config "postgresql-server-dev-${PG_MAJOR}"

ENV RUSTUP_HOME=/opt/rustup CARGO_HOME=/opt/cargo PATH=/opt/cargo/bin:$PATH
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
      sh -s -- -y --profile minimal --default-toolchain stable

WORKDIR /src
RUN git clone --depth 1 --branch "v${EXT_VERSION}" \
      https://github.com/CrunchyData/pg_parquet.git .

# cargo-pgrx must match the pgrx version pinned in Cargo.toml.
RUN cargo install --locked cargo-pgrx \
      --version "$(sed -n 's/^pgrx = "=\(.*\)"/\1/p' Cargo.toml)" && \
    cargo pgrx init "--pg${PG_MAJOR}" "$(command -v pg_config)" && \
    cargo pgrx install --release --no-default-features \
      --features "pg${PG_MAJOR}" --pg-config "$(command -v pg_config)"

RUN mkdir -p /licenses/pg-parquet && cp LICENSE /licenses/pg-parquet/

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /licenses /licenses/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_parquet.so /lib/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_parquet* /share/extension/

USER 65532:65532
