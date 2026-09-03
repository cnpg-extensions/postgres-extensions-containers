# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "snakeoil"
  sql_name                 = "pg_snakeoil"
  image_name               = "snakeoil"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = []
  postgresql_parameters    = { "pg_snakeoil.signature_dir" = "/extensions/snakeoil/share/clamav" }
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-snakeoil
        package = "1.4-3.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-snakeoil extractVersion=^(?<version>\d+)
        sql     = "1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-snakeoil
        package = "1.4-3.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-snakeoil extractVersion=^(?<version>\d+)
        sql     = "1"
      }
    }
  }
}
