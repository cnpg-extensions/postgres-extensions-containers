# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-partman"
  sql_name                 = "pg_partman"
  image_name               = "pg-partman"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_partman_bgw"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-partman
        package = "5.5.0-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-partman extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "5.5.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-partman
        package = "5.5.0-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-partman extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "5.5.0"
      }
    }
  }
}
