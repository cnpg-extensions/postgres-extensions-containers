# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-rage-terminator"
  sql_name                 = "pg_rage_terminator"
  image_name               = "pg-rage-terminator"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_rage_terminator"]
  postgresql_parameters    = {
    "pg_rage_terminator.chance" = "0"
  }
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = false
  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=pg-rage-terminator-18
        package = "0.1.7-12.pgdg12+2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=pg-rage-terminator-18
        package = "0.1.7-12.pgdg13+2"
      }
    }
  }
}
