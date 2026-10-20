variable "environment" {
  default = "testing"
  validation {
    condition = contains(["testing", "production"], environment)
    error_message = "environment must be either testing or production"
  }
}

variable "registry" {
  default = "localhost:5000"
}

variable "revision" {
  default = ""
}

variable "DISTRO" {
  default = ""
}

fullname = (environment == "testing") ? "${registry}/${metadata.image_name}-testing" : "${registry}/${metadata.image_name}"
variable "build_timestamp" {
  default = ""
  validation {
    condition = build_timestamp != ""
    error_message = "build_timestamp must be supplied by preparation"
  }
}
variable "sbom_generator" {
  default = ""
  validation {
    condition = can(regex("@sha256:[a-f0-9]{64}$", sbom_generator))
    error_message = "sbom_generator must be digest-qualified"
  }
}
now = build_timestamp
authors = "The CNPG Extensions Contributors"
url = "https://github.com/cnpg-extensions/postgres-extensions-containers"

target "default" {
  matrix = {
    build = getBuildMatrix()
  }

  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
  dockerfile = "${metadata.name}/Dockerfile"
  name = getBuildName(metadata.name, build.distro, build.pgVersion)

  tags = [
    "${getImageName(fullname)}:${getExtensionVersion(build.distro, build.pgVersion)}-${build.pgVersion}-${build.distro}",
    "${getImageName(fullname)}:${getExtensionVersion(build.distro, build.pgVersion)}-${formatdate("YYYYMMDDhhmm", now)}-${build.pgVersion}-${build.distro}",
  ]

  args = {
    PG_MAJOR = "${build.pgVersion}"
    EXT_VERSION = "${getExtensionPackage(build.distro, build.pgVersion)}"
    BASE = "${getBaseImage(build.distro, build.pgVersion)}"
  }

  output = ["type=image,oci-mediatypes=true,oci-artifact=true"]
  attest = ["type=provenance,mode=max", "type=sbom,generator=${sbom_generator}"]
  annotations = [
    "index,manifest:org.opencontainers.image.created=${now}",
    "index,manifest:org.opencontainers.image.url=${url}",
    "index,manifest:org.opencontainers.image.source=${url}",
    "index,manifest:org.opencontainers.image.version=${getExtensionVersion(build.distro, build.pgVersion)}",
    "index,manifest:org.opencontainers.image.revision=${revision}",
    "index,manifest:org.opencontainers.image.vendor=${authors}",
    "index,manifest:org.opencontainers.image.title=${metadata.name} ${getExtensionVersion(build.distro, build.pgVersion)} ${build.pgVersion} ${build.distro}",
    "index,manifest:org.opencontainers.image.description=A ${metadata.name} ${getExtensionVersion(build.distro, build.pgVersion)} pgrx container image for PostgreSQL ${build.pgVersion} on ${build.distro}",
    "index,manifest:org.opencontainers.image.documentation=${url}",
    "index,manifest:org.opencontainers.image.authors=${authors}",
    "index,manifest:org.opencontainers.image.licenses=${join(" AND ", metadata.licenses)}",
    "index,manifest:org.opencontainers.image.base.name=scratch",
    "index,manifest:io.cloudnativepg.image.base.name=${getBaseImage(build.distro, build.pgVersion)}",
    "index,manifest:io.cloudnativepg.image.base.pgmajor=${build.pgVersion}",
    "index,manifest:io.cloudnativepg.image.base.os=${build.distro}",
    "index,manifest:io.cloudnativepg.image.sql.version=${getExtensionSqlVersion(build.distro, build.pgVersion)}",
  ]
  labels = {
    "org.opencontainers.image.created" = "${now}"
    "org.opencontainers.image.url" = "${url}"
    "org.opencontainers.image.source" = "${url}"
    "org.opencontainers.image.version" = "${getExtensionVersion(build.distro, build.pgVersion)}"
    "org.opencontainers.image.revision" = "${revision}"
    "org.opencontainers.image.vendor" = "${authors}"
    "org.opencontainers.image.title" = "${metadata.name} ${getExtensionVersion(build.distro, build.pgVersion)} ${build.pgVersion} ${build.distro}"
    "org.opencontainers.image.description" = "A ${metadata.name} ${getExtensionVersion(build.distro, build.pgVersion)} pgrx container image for PostgreSQL ${build.pgVersion} on ${build.distro}"
    "org.opencontainers.image.documentation" = "${url}"
    "org.opencontainers.image.authors" = "${authors}"
    "org.opencontainers.image.licenses" = "${join(" AND ", metadata.licenses)}"
    "org.opencontainers.image.base.name" = "scratch"
    "io.cloudnativepg.image.base.name" = "${getBaseImage(build.distro, build.pgVersion)}"
    "io.cloudnativepg.image.base.pgmajor" = "${build.pgVersion}"
    "io.cloudnativepg.image.base.os" = "${build.distro}"
    "io.cloudnativepg.image.sql.version" = "${getExtensionSqlVersion(build.distro, build.pgVersion)}"
  }
}

function getImageName {
  params = [name]
  result = lower(name)
}

function getBuildName {
  params = [extName, distro, pgVersion]
  result = format("%s-%s-%s-%s", extName, sanitize(getExtensionVersion(distro, pgVersion)), pgVersion, distro)
}

function getBuildMatrix {
  params = []
  result = flatten([
    for distroName in keys(metadata.versions) : [
      for pgVersion in keys(metadata.versions[distroName]) : {
        distro = distroName
        pgVersion = pgVersion
      } if DISTRO == "" || distroName == DISTRO
    ]
  ])
}

function getExtensionPackage {
  params = [distro, pgVersion]
  result = metadata.versions[distro][pgVersion]["package"]
}

function getExtensionSqlVersion {
  params = [distro, pgVersion]
  result = lookup(metadata.versions[distro][pgVersion], "sql", "")
}

function getExtensionVersion {
  params = [distro, pgVersion]
  result = getExtensionPackage(distro, pgVersion)
}

function getBaseImage {
  params = [distro, pgVersion]
  result = format("ghcr.io/cloudnative-pg/postgresql:%s-minimal-%s", pgVersion, distro)
}
