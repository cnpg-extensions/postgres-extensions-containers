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
ADD https://github.com/supabase/pg_jsonschema/archive/${EXT_VERSION}.tar.gz /tmp/source.tar.gz
RUN /pgrx/verify-source.sh && tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build

RUN /pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}" /build/Cargo.lock

# The pgrx build arguments mirror the upstream command:
# https://github.com/supabase/pg_jsonschema/blob/v0.3.4/.github/workflows/release.yml#L61-L63
RUN cargo pgrx package \
      --no-default-features \
      --features pg${PG_MAJOR}

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
COPY --from=builder /build/target/release/pg_jsonschema-pg${PG_MAJOR}/usr/lib/postgresql/${PG_MAJOR}/lib/pg_jsonschema.so /lib/

# Share
COPY --from=builder /build/target/release/pg_jsonschema-pg${PG_MAJOR}/usr/share/postgresql/${PG_MAJOR}/extension/pg_jsonschema* /share/extension/

USER 65532:65532
