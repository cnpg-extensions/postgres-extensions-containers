# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "unit"
  sql_name                 = "unit"
  image_name               = "unit"
  licenses                 = ["GPL-3.0-or-later"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = ["base-image:plpgsql"]
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-unit
        package = "7.10-2.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-unit extractVersion=^(?<version>\d+)
        sql     = "7"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-unit
        package = "7.10-2.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-unit extractVersion=^(?<version>\d+)
        sql     = "7"
      }
    }
  }
}
