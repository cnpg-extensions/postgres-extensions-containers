# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pglogical"
  sql_name                 = "pglogical"
  image_name               = "pglogical"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pglogical"]
  postgresql_parameters    = {
    "wal_level" = "logical"
    "output_plugin_libraries" = "pgoutput,test_decoding,pglogical_output"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pglogical
        package = "2.4.8-2.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pglogical extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.4.8"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pglogical
        package = "2.4.8-2.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pglogical extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.4.8"
      }
    }
  }
}
