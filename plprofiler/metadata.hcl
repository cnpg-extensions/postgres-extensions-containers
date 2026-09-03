# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "plprofiler"
  sql_name                 = "plprofiler"
  image_name               = "plprofiler"
  licenses                 = ["Artistic-2.0"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-plprofiler
        package = "4.2.5-4.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-plprofiler extractVersion=^(?<version>\d+\.\d+)
        sql     = "4.2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-plprofiler
        package = "4.2.5-4.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-plprofiler extractVersion=^(?<version>\d+\.\d+)
        sql     = "4.2"
      }
    }
  }
}
