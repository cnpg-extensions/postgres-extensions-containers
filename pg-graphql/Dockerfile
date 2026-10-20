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
# EXT_VERSION is the exact upstream Git tag; preserve its v prefix.
ADD https://github.com/supabase/pg_graphql/archive/${EXT_VERSION}.tar.gz /tmp/source.tar.gz
RUN /pgrx/verify-source.sh && tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build
RUN /pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}" /build/Cargo.lock
# This is the upstream release build command:
# https://github.com/supabase/pg_graphql/blob/v1.6.2/dockerfiles/db/Dockerfile#L37-L38
RUN cargo pgrx install --release --features pg${PG_MAJOR}

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
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_graphql.so /lib/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_graphql* /share/extension/

USER 65532:65532
