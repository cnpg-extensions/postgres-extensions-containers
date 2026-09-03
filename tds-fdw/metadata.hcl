# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "tds-fdw"
  sql_name                 = "tds_fdw"
  image_name               = "tds-fdw"
  licenses                 = ["PostgreSQL"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-tds-fdw
        package = "2.0.5-2.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-tds-fdw extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.0.5"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-tds-fdw
        package = "2.0.5-2.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-tds-fdw extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.0.5"
      }
    }
  }
}
