# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-hint-plan"
  sql_name                 = "pg_hint_plan"
  image_name               = "pg-hint-plan"
  licenses                 = ["NTT"]
  shared_preload_libraries = ["pg_hint_plan"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-hint-plan
        package = "1.8.1-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-hint-plan extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.8.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-hint-plan
        package = "1.8.1-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-hint-plan extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.8.1"
      }
    }
  }
}
