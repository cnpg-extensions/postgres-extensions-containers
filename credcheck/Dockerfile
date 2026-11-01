# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

RUN apt-get update && apt-get install -y --no-install-recommends \
      "postgresql-${PG_MAJOR}-credcheck=${EXT_VERSION}"

# Renovate maps package X.Y to SQL X.Y.0; fail if upstream changes that convention.
RUN grep -Eq "^default_version[[:space:]]*=[[:space:]]*'[0-9]+\.[0-9]+\.0'[[:space:]]*$" \
      "/usr/share/postgresql/${PG_MAJOR}/extension/credcheck.control" \
    || { echo "credcheck SQL version no longer follows X.Y.0; review the Renovate mapping" >&2; exit 1; }

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-credcheck/copyright /licenses/postgresql-${PG_MAJOR}-credcheck/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/credcheck.so /lib/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/bitcode/ /lib/bitcode/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/credcheck* /share/extension/

USER 65532:65532
