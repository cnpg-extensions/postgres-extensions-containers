# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-squeeze"
  sql_name                 = "pg_squeeze"
  image_name               = "pg-squeeze"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_squeeze"]
  postgresql_parameters    = {
    max_replication_slots    = "1"
    output_plugin_libraries  = "pg_squeeze"
    wal_level                = "logical"
  }
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-squeeze
        package = "1.9.4-2.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-squeeze extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.9"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-squeeze
        package = "1.9.4-2.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-squeeze extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.9"
      }
    }
  }
}