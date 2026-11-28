# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "hll"
  sql_name                 = "hll"
  image_name               = "hll"
  licenses                 = ["Apache-2.0"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-hll
        package = "2.21-2.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-hll extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.21"
      }
      "19" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-19-hll
        package = "2.21-1.pgdg12+3"
        // renovate: suite=bookworm-pgdg depName=postgresql-19-hll extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.21"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-hll
        package = "2.21-2.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-hll extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.21"
      }
      "19" = {
        // renovate: suite=trixie-pgdg depName=postgresql-19-hll
        package = "2.21-1.pgdg13+3"
        // renovate: suite=trixie-pgdg depName=postgresql-19-hll extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.21"
      }
    }
  }
}
