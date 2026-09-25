# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "plpgsql-check"
  sql_name                 = "plpgsql_check"
  image_name               = "plpgsql-check"
  licenses                 = ["MIT"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-plpgsql-check
        package = "2.10.10-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-plpgsql-check extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.10"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-plpgsql-check
        package = "2.10.10-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-plpgsql-check extractVersion=^(?<version>\d+\.\d+)
        sql     = "2.10"
      }
    }
  }
}
