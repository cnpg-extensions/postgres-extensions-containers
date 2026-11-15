# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pljs"
  sql_name                 = "pljs"
  image_name               = "pljs"
  licenses                 = ["LicenseRef-PLJS"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pljs
        package = "1.0.5-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pljs extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.0.5"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pljs
        package = "1.0.5-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pljs extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.0.5"
      }
    }
  }
}
