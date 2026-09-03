# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "debversion"
  sql_name                 = "debversion"
  image_name               = "debversion"
  licenses                 = ["GPL-3+"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-debversion
        package = "1.2.0-3.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-debversion extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-debversion
        package = "1.2.0-3.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-debversion extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.2"
      }
    }
  }
}
