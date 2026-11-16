# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder
ARG PG_MAJOR
ARG EXT_VERSION
USER 0
RUN apt-get update && apt-get install -y --no-install-recommends "postgresql-${PG_MAJOR}-pgfaceting=${EXT_VERSION}"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-pgfaceting/copyright /licenses/postgresql-${PG_MAJOR}-pgfaceting/

# Libraries
# This SQL-only extension has no shared objects.

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pgfaceting* /share/extension/

USER 65532:65532
