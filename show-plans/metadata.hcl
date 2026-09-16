# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "show-plans"
  sql_name                 = "pg_show_plans"
  image_name               = "show-plans"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_show_plans"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-show-plans
        package = "2.1.8-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-show-plans extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-show-plans
        package = "2.1.8-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-show-plans extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.1"
      }
    }
  }
}
