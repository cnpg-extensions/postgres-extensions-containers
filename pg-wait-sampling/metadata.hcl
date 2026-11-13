# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-wait-sampling"
  sql_name                 = "pg_wait_sampling"
  image_name               = "pg-wait-sampling"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_wait_sampling"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-wait-sampling
        package = "1.1.11-1.pgdg12+2"
          // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-wait-sampling extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
          sql     = "1.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-wait-sampling
        package = "1.1.11-1.pgdg13+2"
          // renovate: suite=trixie-pgdg depName=postgresql-18-pg-wait-sampling extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
          sql     = "1.1"
      }
    }
  }
}
