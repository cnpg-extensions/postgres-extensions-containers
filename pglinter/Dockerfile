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
ADD https://github.com/pmpetit/pglinter/archive/${EXT_VERSION}.tar.gz /tmp/source.tar.gz
RUN tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build

# 2.0.0 omits Cargo.lock. Borrow the first upstream lockfile, which still
# describes 2.0.0 and pgrx 0.18.0. Manually review/remove on the next release;
# never overwrite a lockfile supplied by upstream. See WORKAROUNDS.md.
RUN { test "${EXT_VERSION}" = 2.0.0 && test ! -e Cargo.lock && \
      echo '6d54556b70b1f82cd2c316b65c8ff79049acea8b27a067320554914a4cbb731d  Cargo.toml' | sha256sum --check --strict -; } \
    || { echo 'Upstream pglinter release changed: manually review/remove the borrowed Cargo.lock' >&2; exit 1; }
ADD --checksum=sha256:01e53fa8890c497dc1b52cc75ef4ad4ecdadf996c22ad510ec6232f3a7ec0dca https://raw.githubusercontent.com/pmpetit/pglinter/d76a73d631b5435843917154a86e40c9d3889740/Cargo.lock /build/Cargo.lock

RUN /pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}" /build/Cargo.lock

# Keep the upstream release profile (fat LTO) on both architectures; native
# ARM64 runner validation and the difference from upstream CI are in WORKAROUNDS.md.
# https://github.com/pmpetit/pglinter/blob/2.0.0/Makefile#L255-L262
RUN cargo pgrx package --pg-config /usr/lib/postgresql/${PG_MAJOR}/bin/pg_config --profile release

ARG PGRX_BUILD_TIMESTAMP
RUN /pgrx/finalize-pgrx-evidence.sh

FROM scratch AS pgrx-sbom
COPY --from=builder /build/pgrx-sbom/ /pgrx-sbom/

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /build/pgrx-licenses/rust/ /licenses/rust/

# Libraries and SQL
COPY --from=builder /build/target/release/pglinter-pg${PG_MAJOR}/usr/lib/postgresql/${PG_MAJOR}/lib/pglinter.so /lib/
COPY --from=builder /build/target/release/pglinter-pg${PG_MAJOR}/usr/share/postgresql/${PG_MAJOR}/extension/pglinter* /share/extension/

USER 65532:65532
