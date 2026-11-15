# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "rational"
  sql_name                 = "pg_rational"
  image_name               = "rational"
  licenses                 = ["MIT"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-rational
        package = "0.0.3-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-rational extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.0.3"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-rational
        package = "0.0.3-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-rational extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.0.3"
      }
    }
  }
}
