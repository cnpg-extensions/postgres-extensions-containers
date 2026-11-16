# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-stat-tcpinfo"
  sql_name                 = "pg_stat_tcpinfo"
  image_name               = "pg-stat-tcpinfo"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-stat-tcpinfo
        package = "1.1-2.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-stat-tcpinfo extractVersion=^(?<version>\d+\.\d+)-
        sql     = "1.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-tcpinfo
        package = "1.1-2.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-stat-tcpinfo extractVersion=^(?<version>\d+\.\d+)-
        sql     = "1.1"
      }
    }
  }
}
