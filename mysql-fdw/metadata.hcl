# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "mysql-fdw"
  sql_name                 = "mysql_fdw"
  image_name               = "mysql-fdw"
  licenses                 = ["BSD-3-Clause"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = true
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-mysql-fdw
        package = "2.9.3-2.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-mysql-fdw extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.9.3"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-mysql-fdw
        package = "2.9.3-2.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-mysql-fdw extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.9.3"
      }
    }
  }
}
