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
WORKDIR /build
ADD https://github.com/neondatabase/pg_session_jwt/archive/${EXT_VERSION}.tar.gz /tmp/source.tar.gz
RUN /pgrx/verify-source.sh && tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build

# v0.5.0 ships the previous package version. Review/remove this correction
# whenever upstream changes, even if the source checksum lock was refreshed.
RUN echo '07d0e4d27a45de2fcad92b955b058723e8266050c1ad4eba2497adb8f55c7aa1  Cargo.lock' | sha256sum --check --strict - \
    || { echo 'Upstream Cargo.lock changed: review/remove the pg-session-jwt version correction' >&2; exit 1; }
RUN cp Cargo.lock /tmp/pgrx-original-Cargo.lock && \
    sed -i '/^name = "pg_session_jwt"$/{n;s/^version = "0.4.0"$/version = "0.5.0"/;}' Cargo.lock && \
    ! cmp -s /tmp/pgrx-original-Cargo.lock Cargo.lock && \
    echo '262845e77a113cf8d81fde7517d04df81f5f694d63a0c848fed72ff5b4390434  Cargo.lock' | sha256sum --check --strict -

RUN /pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}" /build/Cargo.lock

# The upstream build example in Issue #28 uses `cargo pgrx install --release`:
# https://github.com/neondatabase/pg_session_jwt/issues/28#issuecomment-2685604932
# https://github.com/neondatabase/neon/blob/fa504217c61bbcaf5c512d75830564541f917f8f/compute/compute-node.Dockerfile#L1380
RUN cargo pgrx install --release

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
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_session_jwt.so /lib/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_session_jwt* /share/extension/

USER 65532:65532
