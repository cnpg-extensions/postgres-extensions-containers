# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                       = "table-log"
  sql_name                   = "table_log"
  image_name                 = "table-log"
  licenses                   = ["LicenseRef-table-log"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-tablelog
        package = "0.6.4-4.pgdg12+3"
        // SQL catalog version is read from the packaged control file; review separately from package updates.
        sql = "0.6.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-tablelog
        package = "0.6.4-4.pgdg13+3"
        // SQL catalog version is read from the packaged control file; review separately from package updates.
        sql = "0.6.1"
      }
    }
  }
}
