# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pgsentinel"
  sql_name                 = "pgsentinel"
  image_name               = "pgsentinel"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_stat_statements", "pgsentinel"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgsentinel
        package = "1.5.0-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgsentinel extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.5.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgsentinel
        package = "1.5.0-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgsentinel extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.5.0"
      }
    }
  }
}