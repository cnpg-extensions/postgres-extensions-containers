# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "semver"
  sql_name                 = "semver"
  image_name               = "semver"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-semver
        package = "0.42.0-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-semver extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.42.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-semver
        package = "0.42.0-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-semver extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.42.0"
      }
    }
  }
}
