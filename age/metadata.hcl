# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "age"
  sql_name                 = "age"
  image_name               = "age"
  licenses                 = ["Apache-2.0", "LGPL-2.1"]
  shared_preload_libraries = ["age"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-age
        package = "1.8.0~rc0-2.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-age extractVersion=^(?<version>[\d.]+)
        sql     = "1.8.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-age
        package = "1.8.0~rc0-2.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-age extractVersion=^(?<version>[\d.]+)
        sql     = "1.8.0"
      }
    }
  }
}
