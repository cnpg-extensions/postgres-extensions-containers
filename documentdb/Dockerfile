# syntax=docker/dockerfile:1
# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder
ARG PG_MAJOR
ARG EXT_VERSION
USER 0

# Install extension via `apt-get`
RUN apt-get update && apt-get install -y --no-install-recommends \
      "postgresql-${PG_MAJOR}-documentdb=${EXT_VERSION}"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-documentdb/copyright /licenses/postgresql-${PG_MAJOR}-documentdb/

# The distributed component requires Citus.
COPY --from=builder --parents --exclude=**/pg_documentdb_distributed* /usr/lib/postgresql/${PG_MAJOR}/lib/./pg_documentdb*.so /lib/
COPY --from=builder --parents --exclude=**/pg_documentdb_distributed* /usr/lib/postgresql/${PG_MAJOR}/lib/./bitcode/pg_documentdb* /lib/
COPY --from=builder --parents --exclude=**/documentdb_distributed* /usr/share/postgresql/${PG_MAJOR}/extension/./documentdb* /share/extension/

USER 65532:65532
