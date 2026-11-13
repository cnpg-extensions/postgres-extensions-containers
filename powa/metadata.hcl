# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "powa"
  sql_name                 = "powa"
  image_name               = "powa"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_stat_statements", "powa"]
  postgresql_parameters    = {
  }
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = ["base-image:pg_stat_statements", "base-image:btree_gist"]
  create_extension         = true
  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-powa
        package = "5.3.0-1.pgdg12+3"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-powa extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "5.3.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-powa
        package = "5.3.0-1.pgdg13+3"
        // renovate: suite=trixie-pgdg depName=postgresql-18-powa extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "5.3.0"
      }
    }
  }
}
