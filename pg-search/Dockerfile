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
ARG PGRX_SOURCE_REPOSITORY
ARG PGRX_SOURCE_REVISION

USER 0

COPY pgrx/ /pgrx/
WORKDIR /build
ADD https://github.com/paradedb/paradedb/archive/${EXT_VERSION}.tar.gz /tmp/source.tar.gz
RUN tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build

# ParadeDB builds with LLD and OpenBLAS:
# https://github.com/paradedb/paradedb/blob/v0.26.6/docker/Dockerfile.source#L16-L19
RUN apt-get update && apt-get install -y --no-install-recommends lld libopenblas-dev
RUN /pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}" /build/Cargo.lock

# ParadeDB packages from the pg_search workspace directory:
# https://github.com/paradedb/paradedb/blob/v0.26.6/.github/workflows/publish-pg_search-debian.yml#L300-L307
RUN cd pg_search && cargo pgrx package

ARG PGRX_BUILD_TIMESTAMP
RUN /pgrx/finalize-pgrx-evidence.sh

FROM scratch AS pgrx-sbom
# Do not remove this line; the finalizer generates the SBOM material automatically.
COPY --from=builder /build/pgrx-sbom/ /pgrx-sbom/

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /build/pgrx-licenses/rust/ /licenses/rust/

# Libraries
COPY --from=builder /build/target/release/pg_search-pg${PG_MAJOR}/usr/lib/postgresql/${PG_MAJOR}/lib/pg_search.so /lib/

# Share
COPY --from=builder /build/target/release/pg_search-pg${PG_MAJOR}/usr/share/postgresql/${PG_MAJOR}/extension/pg_search* /share/extension/

USER 65532:65532
