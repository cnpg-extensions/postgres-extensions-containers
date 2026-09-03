# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "h3"
  sql_name                 = "h3"
  image_name               = "h3"
  licenses                 = ["Apache-2.0"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = true
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-h3
        package = "4.2.3-4.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-h3 extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "4.2.3"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-h3
        package = "4.2.3-4.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-h3 extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "4.2.3"
      }
    }
  }
}
