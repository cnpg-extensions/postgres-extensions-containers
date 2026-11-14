# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0

ARG BUILDKIT_SBOM_SCAN_STAGE=builder
ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM ${BASE} AS builder

ARG PG_MAJOR
ARG EXT_VERSION
ARG TARGETARCH
ARG TARGETPLATFORM
ARG PGRX_EXTENSION
ARG PGRX_DISTRO

USER 0

COPY source-build/ /source-build/
WORKDIR /build

# The source archive is selected by the exact upstream Git tag.
ENV PGRX_SOURCE_REPOSITORY=https://github.com/CrunchyData/pg_parquet
ADD ${PGRX_SOURCE_REPOSITORY}/archive/${EXT_VERSION}.tar.gz /tmp/source.tar.gz
RUN tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build

RUN /source-build/pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}" /build/Cargo.lock

# Upstream package command: https://github.com/CrunchyData/pg_parquet/blob/v0.5.1/Makefile#L40-L41
RUN cargo pgrx package \
      --profile release \
      --features pg${PG_MAJOR} \
      --no-default-features

ARG PGRX_BUILD_TIMESTAMP
RUN /source-build/pgrx/finalize-pgrx-evidence.sh

FROM scratch AS pgrx-sbom
# Do not remove this line: the finalizer generates the SBOM material automatically.
COPY --from=builder /build/pgrx-sbom/ /pgrx-sbom/

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /build/pgrx-licenses/rust/ /licenses/rust/

# Libraries
COPY --from=builder /build/target/release/pg_parquet-pg${PG_MAJOR}/usr/lib/postgresql/${PG_MAJOR}/lib/pg_parquet.so /lib/

# Share
COPY --from=builder /build/target/release/pg_parquet-pg${PG_MAJOR}/usr/share/postgresql/${PG_MAJOR}/extension/pg_parquet* /share/extension/

USER 65532:65532
