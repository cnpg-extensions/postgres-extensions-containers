# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

RUN set -eux && \
	ldconfig -p | awk '{print $NF}' | grep '^/' | sort | uniq > /tmp/base-image-libs.out && \
	apt-get update && \
	apt-get install -y --no-install-recommends "postgresql-${PG_MAJOR}-snakeoil=${EXT_VERSION}"

RUN mkdir -p /system /licenses /clamav && \
	ldd /usr/lib/postgresql/${PG_MAJOR}/lib/pg_snakeoil.so \
		| awk '{print $3}' | grep '^/' | sort | uniq > /tmp/all-deps.out && \
	comm -13 /tmp/base-image-libs.out /tmp/all-deps.out > /tmp/libraries.out && \
	while read -r lib; do \
		resolved=$(readlink -f "$lib"); \
		dir=$(dirname "$lib"); \
		base=$(basename "$lib"); \
		cp -a "$resolved" /system/; \
		for file in "$dir"/"${base%.so*}.so"*; do \
			[ -e "$file" ] || continue; \
			if [ -L "$file" ] && [ "$(readlink -f "$file")" = "$resolved" ]; then \
				target=$(basename "$file"); \
				if [ "$target" != "$(basename "$resolved")" ]; then \
					ln -sf "$(basename "$resolved")" "/system/$target"; \
				fi; \
			fi; \
		done; \
	done < /tmp/libraries.out && \
	for lib in $(find /system -maxdepth 1 -type f -name '*.so*'); do \
		pkg=$(dpkg -S "$(basename "$lib")" | grep -v "diversion by" | awk -F: '/:/{print $1; exit}'); \
		[ -z "$pkg" ] && continue; \
		mkdir -p "/licenses/$pkg" && cp -a "/usr/share/doc/$pkg/copyright" "/licenses/$pkg/copyright"; \
	done && \
	printf '44d88612fea8a8f36de82e1278abb02f:68:Eicar-Test-Signature\n' > /clamav/stub.hdb

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /licenses /licenses/
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-snakeoil/copyright /licenses/postgresql-${PG_MAJOR}-snakeoil/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_snakeoil.so /lib/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/bitcode/ /lib/bitcode/

# System libs
COPY --from=builder /system /system/

# ClamAV stub database (minimal signatures to satisfy libclamav at init)
COPY --from=builder /clamav/ /share/clamav/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_snakeoil* /share/extension/

USER 65532:65532
