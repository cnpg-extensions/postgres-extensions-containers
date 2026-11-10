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
ADD https://gitlab.com/dalibo/postgresql_anonymizer/-/archive/${EXT_VERSION}/postgresql_anonymizer-${EXT_VERSION}.tar.gz /tmp/source.tar.gz
RUN tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build
# 3.3.2 retains 3.3.1 for the root package in Cargo.lock. Review/remove on update.
RUN echo 'dc76277a2144f415409a8f8be6ce553908e83b01c02d18aeeb1d7d44c69c4fd6  Cargo.lock' | sha256sum --check --strict - \
    || { echo 'Upstream Cargo.lock changed: review/remove the anon version correction' >&2; exit 1; }
RUN cp Cargo.lock /tmp/pgrx-original-Cargo.lock && \
    sed -i '/^name = "anon"$/{n;s/^version = "3.3.1"$/version = "3.3.2"/;}' Cargo.lock && \
    ! cmp -s /tmp/pgrx-original-Cargo.lock Cargo.lock && \
    echo '2a30c53c32de09d29aed744677dab082396ff6c91c27664fbe32d3b1117b0e42  Cargo.lock' | sha256sum --check --strict -

RUN /pgrx/install-pgrx-build-environment.sh "${PG_MAJOR}" /build/Cargo.lock
# The upstream extension target packages anon and installs its runtime CSV data:
# https://gitlab.com/dalibo/postgresql_anonymizer/-/blob/3.3.2/Makefile
RUN make extension PGVER=pg${PG_MAJOR} PG_CONFIG=/usr/lib/postgresql/${PG_MAJOR}/bin/pg_config

# Do not remove this line: the finalizer generates the SBOM material
# automatically.
ARG PGRX_BUILD_TIMESTAMP
RUN /pgrx/finalize-pgrx-evidence.sh

FROM scratch AS pgrx-sbom
COPY --from=builder /build/pgrx-sbom/ /pgrx-sbom/

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /build/pgrx-licenses/rust/ /licenses/rust/

# Libraries
COPY --from=builder /build/target/release/anon-pg${PG_MAJOR}/usr/lib/postgresql/${PG_MAJOR}/lib/anon.so /lib/

# Share
COPY --from=builder /build/target/release/anon-pg${PG_MAJOR}/usr/share/postgresql/${PG_MAJOR}/extension/anon.control /build/target/release/anon-pg${PG_MAJOR}/usr/share/postgresql/${PG_MAJOR}/extension/anon--*.sql /share/extension/

COPY --from=builder /build/target/release/anon-pg${PG_MAJOR}/usr/share/postgresql/${PG_MAJOR}/extension/anon/ /share/extension/anon/

USER 65532:65532
