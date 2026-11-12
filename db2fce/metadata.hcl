# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "db2fce"
  sql_name                 = "db2fce"
  image_name               = "db2fce"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-db2fce
        package = "0.0.17-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-db2fce extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.0.17"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-db2fce
        package = "0.0.17-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-db2fce extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.0.17"
      }
    }
  }
}
