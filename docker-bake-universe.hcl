// Load after docker-bake.hcl for Universe recipes.
variable "build_timestamp" {
  default = ""
}
now = build_timestamp

function getExtensionVersion {
  params = [distro, pgVersion]
  result = trimprefix(getExtensionPackage(distro, pgVersion), "v")
}

target "default" {
  matrix = {
    build = getBuildMatrix()
  }
  name = getBuildName(metadata.name, build.distro, build.pgVersion)
  dockerfile = "universe/${metadata.name}/Dockerfile"
  args = {
    SOURCE_REPOSITORY = metadata.source_repository
    BUILD_TIMESTAMP = build_timestamp
  }
}
