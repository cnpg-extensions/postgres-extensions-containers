# syntax=docker/dockerfile:1.7

# Python 3.14 is the newest version supported by the pinned ScanCode 32.5.0.
# Move to a newer Python as soon as ScanCode supports it; keep this aligned with SCANCODE_VERSION.
# https://github.com/aboutcode-org/scancode-toolkit/releases/tag/v32.5.0
# renovate: datasource=docker depName=python packageName=library/python versioning=docker
FROM python:3.14-slim-bookworm

ARG TARGETARCH
# renovate: datasource=github-releases depName=anchore/syft versioning=semver
ARG SYFT_VERSION=1.51.1
# renovate: datasource=pypi depName=scancode-toolkit versioning=pep440
ARG SCANCODE_VERSION=32.5.0

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates curl gcc g++ libxml2-dev libxslt1-dev pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && curl --fail --silent --show-error --location \
      "https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}/syft_${SYFT_VERSION}_linux_${TARGETARCH}.tar.gz" \
      | tar -xz -C /usr/local/bin syft \
    && python -m pip install --no-cache-dir "scancode-toolkit==${SCANCODE_VERSION}" \
    && syft version

WORKDIR /opt/cnpg-sbom-generator
COPY compose.py generator.py hooks.py ./

ARG SBOM_GENERATOR_REVISION=unknown
ENV SBOM_GENERATOR_REVISION=${SBOM_GENERATOR_REVISION}
LABEL org.opencontainers.image.revision=${SBOM_GENERATOR_REVISION}

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python3", "/opt/cnpg-sbom-generator/generator.py"]
