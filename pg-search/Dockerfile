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

COPY \
    pgrx/install-pgrx-build-environment.sh \
    pgrx/verify-source.sh \
    pgrx/install_tools.py \
    pgrx/locked_download.py \
    pgrx/build_config.py \
    pgrx/evidence.py \
    pgrx/finalize-pgrx-evidence.sh \
    pgrx/license-about.toml \
    /pgrx/
COPY pgrx/dependencies/apt/ /pgrx/dependencies/apt/
COPY pgrx/dependencies/tools.json pgrx/dependencies/sources.json /pgrx/dependencies/
COPY pgrx/sbom/ /pgrx/sbom/
COPY scripts/capture_base_image_libs.sh scripts/stage_system_libs.sh /usr/local/bin/
RUN capture_base_image_libs.sh
WORKDIR /build
ADD https://github.com/paradedb/paradedb/archive/${EXT_VERSION}.tar.gz /tmp/source.tar.gz
RUN /pgrx/verify-source.sh && tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build

# ParadeDB installs OpenBLAS before packaging pg_search:
# https://github.com/paradedb/paradedb/blob/v0.25.6/.github/workflows/publish-pg_search-debian.yml#L256-L260
# OpenBLAS and its pinned dependencies are installed by the shared helper.
RUN /pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}" /build/Cargo.lock

# ParadeDB packages from the pg_search workspace directory:
# https://github.com/paradedb/paradedb/blob/v0.25.6/.github/workflows/publish-pg_search-debian.yml#L289-L294
RUN cd pg_search && cargo pgrx package
RUN stage_system_libs.sh /build/target/release/pg_search-pg${PG_MAJOR}/usr/lib/postgresql/${PG_MAJOR}/lib/pg_search.so

ARG PGRX_WORKSPACE_SHA256
ARG PGRX_BUILD_TIMESTAMP
RUN /pgrx/finalize-pgrx-evidence.sh

FROM scratch AS pgrx-sbom
# Do not remove this line; the finalizer generates the SBOM material automatically.
COPY --from=builder /build/pgrx-sbom/ /pgrx-sbom/

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /build/pgrx-licenses/rust/ /licenses/rust/
COPY --from=builder /licenses/ /licenses/system/

# Libraries
COPY --from=builder /build/target/release/pg_search-pg${PG_MAJOR}/usr/lib/postgresql/${PG_MAJOR}/lib/pg_search.so /lib/
COPY --from=builder /system/ /system/

# Share
COPY --from=builder /build/target/release/pg_search-pg${PG_MAJOR}/usr/share/postgresql/${PG_MAJOR}/extension/pg_search* /share/extension/

USER 65532:65532
