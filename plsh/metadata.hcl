# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                       = "plsh"
  sql_name                   = "plsh"
  image_name                 = "plsh"
  licenses                   = ["PostgreSQL"]
  shared_preload_libraries   = []
  postgresql_parameters      = {}
  extension_control_path     = []
  dynamic_library_path       = []
  ld_library_path            = []
  bin_path                   = []
  env                        = {}
  auto_update_os_libs        = false
  required_extensions        = []
  create_extension           = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-plsh
        package = "1.20220917-4.pgdg12+3"
        // SQL catalog version is read from the packaged control file; review separately from package updates.
        sql = "2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-plsh
        package = "1.20220917-4.pgdg13+3"
        // SQL catalog version is read from the packaged control file; review separately from package updates.
        sql = "2"
      }
    }
  }
}
