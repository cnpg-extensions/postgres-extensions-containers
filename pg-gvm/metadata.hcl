# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-gvm"
  sql_name                 = "pg-gvm"
  image_name               = "pg-gvm"
  licenses                 = ["GPL-3.0-or-later", "AGPL-3.0-or-later"]
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
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-gvm
        package = "22.6.18-1.pgdg13+1"
        // The PGDG package version is patch-level; SQL control version is 22.6.
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-gvm extractVersion=^(?<version>\d+\.\d+)
        sql     = "22.6"
      }
    }
  }
}
