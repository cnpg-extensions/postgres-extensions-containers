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

# Both fresh installs and upgrades to 1.2-0 run this SQL migration.
RUN <<'SH'
set -eu
cd "/usr/share/postgresql/${PG_MAJOR}/extension"
migration=documentdb--1.1-0--1.2-0.sql
echo "555a09a69a917762ceb1b5b9927ca60cb0c257b4cce25f40f99f08a96675269f  $migration" | sha256sum --check --strict - || {
    echo 'DocumentDB migration changed: review the planner schema grants' >&2
    exit 1
}
# DocumentDB's planner looks up types and functions even for ordinary SQL queries.
# Without schema USAGE, SELECT 1 = 1 can fail with
# "ERROR: permission denied for schema documentdb_core".
cat >> "$migration" <<'SQL'

GRANT USAGE ON SCHEMA documentdb_core, documentdb_api_catalog,
    documentdb_api_internal, documentdb_api TO PUBLIC;
SQL
SH

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-documentdb/copyright /licenses/postgresql-${PG_MAJOR}-documentdb/

COPY --from=builder --parents /usr/lib/postgresql/${PG_MAJOR}/lib/./pg_documentdb*.so /lib/
COPY --from=builder --parents /usr/lib/postgresql/${PG_MAJOR}/lib/./bitcode/pg_documentdb* /lib/
COPY --from=builder --parents /usr/share/postgresql/${PG_MAJOR}/extension/./documentdb* /share/extension/

USER 65532:65532
