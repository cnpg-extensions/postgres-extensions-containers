# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-pwhash"
  sql_name                 = "pg_pwhash"
  image_name               = "pg-pwhash"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-pwhash
        package = "1.0-2.pgdg12+4"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-pwhash extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-pwhash
        package = "1.0-2.pgdg13+4"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-pwhash extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.0"
      }
    }
  }
}
