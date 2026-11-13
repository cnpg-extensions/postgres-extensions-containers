# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pllua"
  sql_name                 = "pllua"
  image_name               = "pllua"
  licenses                 = ["MIT"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pllua
        package = "1:2.0.12-8.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pllua extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
        sql     = "2.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pllua
        package = "1:2.0.12-8.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pllua extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
        sql     = "2.0"
      }
    }
  }
}
