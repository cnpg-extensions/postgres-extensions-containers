# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-qualstats"
  sql_name                 = "pg_qualstats"
  image_name               = "pg-qualstats"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_qualstats"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-qualstats
        package = "2.1.4-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-qualstats extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.1.4"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-qualstats
        package = "2.1.4-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-qualstats extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.1.4"
      }
    }
  }
}
