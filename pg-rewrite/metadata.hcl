# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                       = "pg-rewrite"
  sql_name                   = "pg_rewrite"
  image_name                 = "pg-rewrite"
  licenses                   = ["PostgreSQL"]
  shared_preload_libraries   = ["pg_rewrite"]
  postgresql_parameters      = {"wal_level" = "logical", "output_plugin_libraries" = "pgoutput,test_decoding,pg_rewrite"}
  extension_control_path     = []
  dynamic_library_path       = []
  ld_library_path            = []
  bin_path                   = []
  env                        = {}
  auto_update_os_libs        = false
  required_extensions        = []
  create_extension           = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-rewrite
        package = "2.2-2.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-rewrite extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
        sql = "2.2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-rewrite
        package = "2.2-2.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-rewrite extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
        sql = "2.2"
      }
    }
  }
}
