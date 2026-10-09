# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "orafce"
  sql_name                 = "orafce"
  image_name               = "orafce"
  licenses                 = ["0BSD", "GPL-3.0-or-later WITH Bison-exception-2.2"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-orafce
        package = "4.16.13-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-orafce extractVersion=^(?<version>\d+\.\d+)
        sql     = "4.16"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-orafce
        package = "4.16.13-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-orafce extractVersion=^(?<version>\d+\.\d+)
        sql     = "4.16"
      }
    }
  }
}
