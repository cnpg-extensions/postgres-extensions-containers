# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-background"
  sql_name                 = "pg_background"
  image_name               = "pg-background"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-background
        package = "2.0.3-1.pgdg12+3"
          // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-background extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
          sql     = "2.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-background
        package = "2.0.3-1.pgdg13+3"
          // renovate: suite=trixie-pgdg depName=postgresql-18-pg-background extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
          sql     = "2.0"
      }
    }
  }
}
