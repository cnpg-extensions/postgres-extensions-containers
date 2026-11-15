# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "extra-window-functions"
  sql_name                 = "extra_window_functions"
  image_name               = "extra-window-functions"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-extra-window-functions
        package = "2.0-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-extra-window-functions extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-extra-window-functions
        package = "2.0-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-extra-window-functions extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.0"
      }
    }
  }
}
