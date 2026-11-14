// Load after docker-bake.hcl for non-Rust source recipes.
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
    BUILD_TIMESTAMP = build_timestamp
  }
}
