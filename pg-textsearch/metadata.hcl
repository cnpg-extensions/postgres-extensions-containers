# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-textsearch"
  sql_name                 = "pg_textsearch"
  image_name               = "pg-textsearch"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_textsearch"]
  postgresql_parameters    = { hot_standby_feedback = "on" }
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-textsearch
        package = "1.5.1-3.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-textsearch extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.5.1"
      }
      "19" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-19-pg-textsearch
        package = "1.6.0-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-19-pg-textsearch extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.6.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-textsearch
        package = "1.5.1-3.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-textsearch extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.5.1"
      }
      "19" = {
        // renovate: suite=trixie-pgdg depName=postgresql-19-pg-textsearch
        package = "1.6.0-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-19-pg-textsearch extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.6.0"
      }
    }
  }
}
