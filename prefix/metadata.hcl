# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "prefix"
  sql_name                 = "prefix"
  image_name               = "prefix"
  licenses                 = ["BSD-2-Clause"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-prefix
        package = "1.2.11-1.pgdg12+2"
        // SQL version does not track the Debian package version; review it against the package control file on upgrades.
        sql     = "1.2.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-prefix
        package = "1.2.11-1.pgdg13+2"
        // SQL version does not track the Debian package version; review it against the package control file on upgrades.
        sql     = "1.2.0"
      }
    }
  }
}
