# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-stat-log"
  sql_name                 = "pg_stat_log"
  image_name               = "pg-stat-log"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_stat_log"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-stat-log
        package = "0.3-1.pgdg12+1"
        // SQL version is independent of the package version; inspect control files before merging.
        // Release 0.3 aligned them: https://github.com/fabriziomello/pg_stat_log/pull/7
        sql     = "0.3"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-stat-log
        package = "0.3-1.pgdg13+1"
        // SQL version is independent of the package version; inspect control files before merging.
        // Release 0.3 aligned them: https://github.com/fabriziomello/pg_stat_log/pull/7
        sql     = "0.3"
      }
    }
  }
}
