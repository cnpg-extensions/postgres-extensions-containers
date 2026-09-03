# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "mobilitydb"
  sql_name                 = "mobilitydb"
  image_name               = "mobilitydb"
  licenses                 = ["GPL-2+", "GPL-3+"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = true
  required_extensions      = ["postgis"]
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-mobilitydb
        package = "1.3.0-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-mobilitydb extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.3.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-mobilitydb
        package = "1.3.0-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-mobilitydb extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.3.0"
      }
    }
  }
}
