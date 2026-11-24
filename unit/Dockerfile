# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

# The CNPG base image supplies PostgreSQL and the system runtime libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
      patch \
      "postgresql-${PG_MAJOR}-unit=${EXT_VERSION}"

# PGDG's SQL files hard-code the package's Debian share directory. In a CNPG
# extension image, the data files are mounted below /extensions/unit instead.
COPY unit/patches/0001-use-cnpg-mounted-data-files.patch /tmp/
RUN sed -i "s/@PG_MAJOR@/${PG_MAJOR}/g" /tmp/0001-use-cnpg-mounted-data-files.patch && \
    patch --batch --forward -p1 \
    -d "/usr/share/postgresql/${PG_MAJOR}/extension" \
    < /tmp/0001-use-cnpg-mounted-data-files.patch

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-unit/copyright /licenses/postgresql-${PG_MAJOR}-unit/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/unit* /lib/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/bitcode/ /lib/bitcode/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/unit* /share/extension/

USER 65532:65532
