# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "mimeo"
  sql_name                 = "mimeo"
  image_name               = "mimeo"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = []
  postgresql_parameters    = {
  }
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = ["base-image:dblink"]
  create_extension         = true
  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-mimeo
        package = "1.5.1-20.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-mimeo extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.5.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-mimeo
        package = "1.5.1-20.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-mimeo extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.5.1"
      }
    }
  }
}
