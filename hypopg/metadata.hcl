# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "hypopg"
  sql_name                 = "hypopg"
  image_name               = "hypopg"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-hypopg
        package = "1.4.3-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-hypopg extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.4.3"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-hypopg
        package = "1.4.3-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-hypopg extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "1.4.3"
      }
    }
  }
}
