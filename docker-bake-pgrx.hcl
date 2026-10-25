// Load after docker-bake.hcl: PGRX uses literal source versions.
variable "build_timestamp" {
  default = ""
}

now = build_timestamp

function getExtensionVersion {
  params = [distro, pgVersion]
  result = getExtensionPackage(distro, pgVersion)
}
