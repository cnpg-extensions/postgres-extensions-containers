# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                       = "credcheck"
  sql_name                   = "credcheck"
  image_name                 = "credcheck"
  licenses                   = ["MIT"]
  shared_preload_libraries   = ["credcheck"]
  postgresql_parameters      = { "credcheck.encrypted_password_allowed" = "on" }
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-credcheck
        package = "6.0-1.pgdg12+1"
        // SQL catalog version is read from the packaged control file; review separately from package updates.
        sql = "5.0.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-credcheck
        package = "6.0-1.pgdg13+1"
        // SQL catalog version is read from the packaged control file; review separately from package updates.
        sql = "5.0.0"
      }
    }
  }
}
