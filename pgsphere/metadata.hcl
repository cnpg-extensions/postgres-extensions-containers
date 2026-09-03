# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pgsphere"
  sql_name                 = "pg_sphere"
  image_name               = "pgsphere"
  licenses                 = ["GPL-3+"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgsphere
        package = "1.5.2-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgsphere extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.5.2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgsphere
        package = "1.5.2-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgsphere extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.5.2"
      }
    }
  }
}
