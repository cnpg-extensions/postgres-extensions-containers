# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pgpcre"
  sql_name                 = "pgpcre"
  image_name               = "pgpcre"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgpcre
        package = "0.20190509-9.pgdg12+2"
        // The PGDG release version is date-based and independent of the fixed SQL catalog version.
        sql     = "1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgpcre
        package = "0.20190509-9.pgdg13+2"
        // The PGDG release version is date-based and independent of the fixed SQL catalog version.
        sql     = "1"
      }
    }
  }
}
