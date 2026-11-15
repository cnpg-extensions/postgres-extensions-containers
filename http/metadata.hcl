# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "http"
  sql_name                 = "http"
  image_name               = "http"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-http
        package = "1.7.2-2.pgdg12+3"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-http extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.7"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-http
        package = "1.7.2-2.pgdg13+3"
        // renovate: suite=trixie-pgdg depName=postgresql-18-http extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.7"
      }
    }
  }
}
