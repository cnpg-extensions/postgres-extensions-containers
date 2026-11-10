// Load after docker-bake.hcl: PGRX uses literal source versions.
variable "build_timestamp" {
  default = ""
}

now = build_timestamp

function getExtensionVersion {
  params = [distro, pgVersion]
  result = getExtensionPackage(distro, pgVersion)
}

// The upstream source version is owned by metadata; build inputs are resolved
// per run rather than copied into a second committed source lock.
target "default" {
  matrix = {
    build = getBuildMatrix()
  }
  name = getBuildName(metadata.name, build.distro, build.pgVersion)
  args = {
    PGRX_EXTENSION = metadata.name
    PGRX_DISTRO = build.distro
    PGRX_SOURCE_REPOSITORY = metadata.source_repository
    PGRX_BUILD_TIMESTAMP = build_timestamp
  }
}
