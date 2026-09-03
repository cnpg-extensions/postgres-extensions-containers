# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pgmp"
  sql_name                 = "pgmp"
  image_name               = "pgmp"
  licenses                 = ["LGPL-3+"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = true
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgmp
        package = "1.0.6-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgmp extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgmp
        package = "1.0.6-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgmp extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.1"
      }
    }
  }
}
