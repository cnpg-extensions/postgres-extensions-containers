# SPDX-FileCopyrightText: Copyright © contributors to the Not-CloudNativePG project.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

SHELL ["/bin/bash", "-o", "pipefail", "-c", "-e"]

# Install the release package used by ParadeDB's own extension container.
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl && \
    arch="$(dpkg --print-architecture)" && \
    distro="$(. /etc/os-release && echo "$VERSION_CODENAME")" && \
    case "${distro}/${arch}" in \
      bookworm/amd64) checksum="88bed17a4b7e084ae20ea481ee2e20fa9d210323fc3fc104021bad5cbcb9855f" ;; \
      bookworm/arm64) checksum="8e52aaca5ea79e90617b93e9add11b3d8a8428e2afe9c4617fe5510cf9a043fa" ;; \
      trixie/amd64) checksum="752cd6000bda74f9751bbc41855fd394fda1db58a505db7a52e2b8f134090e0b" ;; \
      trixie/arm64) checksum="3fe3019a0d56e918a9f567c8286a37892187bb5c6e5eae1c53e41beccb651cf0" ;; \
      *) echo "unsupported platform: ${distro}/${arch}" >&2; exit 1 ;; \
    esac && \
    curl -fsSL -o /tmp/pg_search.deb \
      "https://github.com/paradedb/paradedb/releases/download/v${EXT_VERSION}/postgresql-${PG_MAJOR}-pg-search_${EXT_VERSION}-1PARADEDB-${distro}_${arch}.deb" && \
    echo "${checksum}  /tmp/pg_search.deb" | sha256sum -c - && \
    dpkg-query -f '${Package}\n' -W | sort > /tmp/packages.before && \
    apt-get install -y --no-install-recommends /tmp/pg_search.deb && \
    dpkg-query -f '${Package}\n' -W | sort > /tmp/packages.after && \
    comm -13 /tmp/packages.before /tmp/packages.after > /tmp/packages.new && \
    rm /tmp/pg_search.deb && \
    rm -rf /var/lib/apt/lists/*

# Stage only linked libraries introduced by the pg_search package installation.
RUN mkdir -p /system /licenses && \
    ldd "/usr/lib/postgresql/${PG_MAJOR}/lib/pg_search.so" | awk '/=> \//{ print $1, $3 }' | \
    while read -r soname path; do \
        pkg="$(dpkg -S "$(readlink -f "$path")" | awk -F: 'NR == 1 { p = $1 } END { print p }')" || continue; \
        if ! grep -qxF "$pkg" /tmp/packages.new; then continue; fi; \
        cp -L "$path" "/system/${soname}"; \
        if [ -f "/usr/share/doc/${pkg}/copyright" ]; then \
            mkdir -p "/licenses/${pkg}"; \
            cp -L "/usr/share/doc/${pkg}/copyright" "/licenses/${pkg}/"; \
        fi; \
    done

FROM scratch
ARG PG_MAJOR

COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-pg-search/copyright /licenses/postgresql-${PG_MAJOR}-pg-search/
COPY --from=builder /licenses/ /licenses/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_search* /lib/
COPY --from=builder /system/ /system/
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_search* /share/extension/

USER 65532:65532
