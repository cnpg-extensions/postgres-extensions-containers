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
ARG PGRX_SOURCE_SHA256

USER 0

COPY pgrx/ /pgrx/
WORKDIR /build


# EXT_VERSION is the exact upstream Git tag, including its v prefix.
ADD https://github.com/microsoft/pg_durable/archive/${EXT_VERSION}.tar.gz /tmp/source.tar.gz
RUN /pgrx/verify-source.sh && tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build


# Call the shared installer after extracting the source. It derives the
# matching cargo-pgrx version from Cargo.lock and prepares the pgrx/SBOM tools.
RUN /pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}" /build/Cargo.lock


# Upstream package command, adapted only for the shared installer and /build:
# https://github.com/microsoft/pg_durable/blob/v0.2.7/Makefile#L23-L36
RUN cargo pgrx package \
      --out-dir /build/target/release/pg_durable-pg${PG_MAJOR} \
      --no-default-features \
      --features "pg${PG_MAJOR}"


# Do not remove this line: the finalizer generates the SBOM material
# automatically.
ARG PGRX_WORKSPACE_SHA256
ARG PGRX_BUILD_TIMESTAMP
RUN /pgrx/finalize-pgrx-evidence.sh

FROM scratch AS pgrx-sbom
COPY --from=builder /build/pgrx-sbom/ /pgrx-sbom/

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /build/pgrx-licenses/rust/ /licenses/rust/

# Libraries
COPY --from=builder /build/target/release/pg_durable-pg${PG_MAJOR}/usr/lib/postgresql/${PG_MAJOR}/lib/pg_durable.so /lib/

# Share
COPY --from=builder /build/target/release/pg_durable-pg${PG_MAJOR}/usr/share/postgresql/${PG_MAJOR}/extension/pg_durable* /share/extension/

USER 65532:65532
