# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "ip4r"
  sql_name                 = "ip4r"
  image_name               = "ip4r"
  licenses                 = ["PostgreSQL"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-ip4r
        package = "2.4.3-1.pgdg12+3"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-ip4r extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.4"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-ip4r
        package = "2.4.3-1.pgdg13+3"
        // renovate: suite=trixie-pgdg depName=postgresql-18-ip4r extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.4"
      }
    }
  }
}
