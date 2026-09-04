# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "plr"
  sql_name                 = "plr"
  image_name               = "plr"
  licenses                 = ["GPL-2+"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = true
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-plr
        package = "1:8.4.8.6-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-plr extractVersion=^(?:\d+:)?(?<version>[\d.]+)
        sql     = "8.4.8.6"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-plr
        package = "1:8.4.8.6-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-plr extractVersion=^(?:\d+:)?(?<version>[\d.]+)
        sql     = "8.4.8.6"
      }
    }
  }
}
