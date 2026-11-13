# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "icu-ext"
  sql_name                 = "icu_ext"
  image_name               = "icu-ext"
  licenses                 = ["LicenseRef-verite"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-icu-ext
        package = "1.11.0-1.pgdg12+3"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-icu-ext extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.11"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-icu-ext
        package = "1.11.0-1.pgdg13+3"
        // renovate: suite=trixie-pgdg depName=postgresql-18-icu-ext extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.11"
      }
    }
  }
}
