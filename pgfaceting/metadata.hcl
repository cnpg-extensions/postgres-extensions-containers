# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pgfaceting"
  sql_name                 = "pgfaceting"
  image_name               = "pgfaceting"
  licenses                 = ["BSD-3-Clause"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = ["roaringbitmap"]
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgfaceting
        package = "0.2.0-6.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgfaceting extractVersion=^(?<version>\d+\.\d+\.\d+)-
        sql     = "0.2.0"
      }
      "19" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-19-pgfaceting
        package = "0.2.0-6.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-19-pgfaceting extractVersion=^(?<version>\d+\.\d+\.\d+)-
        sql     = "0.2.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgfaceting
        package = "0.2.0-6.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgfaceting extractVersion=^(?<version>\d+\.\d+\.\d+)-
        sql     = "0.2.0"
      }
      "19" = {
        // renovate: suite=trixie-pgdg depName=postgresql-19-pgfaceting
        package = "0.2.0-6.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-19-pgfaceting extractVersion=^(?<version>\d+\.\d+\.\d+)-
        sql     = "0.2.0"
      }
    }
  }
}
