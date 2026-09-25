# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-stat-kcache"
  sql_name                 = "pg_stat_kcache"
  image_name               = "pg-stat-kcache"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_stat_statements", "pg_stat_kcache"]
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = ["base-image:pg_stat_statements"]
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-stat-kcache
        package = "2.3.2-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-stat-kcache extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.3.2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-kcache
        package = "2.3.2-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-kcache extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.3.2"
      }
    }
  }
}