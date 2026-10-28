# syntax=docker/dockerfile:1.28

# renovate: datasource=docker depName=python packageName=library/python versioning=docker
FROM python:3.15-slim-bookworm@sha256:66784ec9700b710e2b1548ab0ad963c118daa61de6804a53b911ff78e819c248

ARG TARGETARCH
# renovate: datasource=github-releases depName=anchore/syft versioning=semver
ARG SYFT_VERSION=1.55.0

# renovate: datasource=pypi depName=spdx-tools versioning=pep440
ARG SPDX_TOOLS_VERSION=0.8.5
COPY dependencies/ /tmp/dependencies/

RUN apt-get update \
    && xargs apt-get install --no-install-recommends -y < "/tmp/dependencies/debian-${TARGETARCH}.txt" \
    && rm -rf /var/lib/apt/lists/* \
    && curl --fail --silent --show-error --location \
      "https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}/syft_${SYFT_VERSION}_linux_${TARGETARCH}.tar.gz" \
      | tar -xz -C /usr/local/bin syft \
    && python -m pip install --no-cache-dir "spdx-tools==${SPDX_TOOLS_VERSION}" \
    && python -m pip check \
    && syft version

WORKDIR /opt/cnpg-sbom-generator
COPY compose.py generator.py hooks.py spdx_validation.py ./

ARG SBOM_GENERATOR_REVISION=unknown
ENV SBOM_GENERATOR_REVISION=${SBOM_GENERATOR_REVISION}
LABEL org.opencontainers.image.revision=${SBOM_GENERATOR_REVISION}

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python3", "/opt/cnpg-sbom-generator/generator.py"]
