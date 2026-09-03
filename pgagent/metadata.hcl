# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pgagent"
  sql_name                 = "pgagent"
  image_name               = "pgagent"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = ["pgagent"]
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=pgagent
        package = "4.2.3-5.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=pgagent extractVersion=^(?<version>\d+\.\d+)
        sql     = "4.2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=pgagent
        package = "4.2.3-5.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=pgagent extractVersion=^(?<version>\d+\.\d+)
        sql     = "4.2"
      }
    }
  }
}
