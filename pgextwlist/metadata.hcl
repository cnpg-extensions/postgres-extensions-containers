# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                       = "pgextwlist"
  sql_name                   = "pgextwlist"
  image_name                 = "pgextwlist"
  licenses                   = ["PostgreSQL"]
  shared_preload_libraries   = ["pgextwlist"]
  postgresql_parameters      = {"extwlist.extensions" = "dblink"}
  extension_control_path     = []
  dynamic_library_path       = []
  ld_library_path            = []
  bin_path                   = []
  env                        = {}
  auto_update_os_libs        = false
  required_extensions        = []
  create_extension           = false

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgextwlist
        package = "1.20-1.pgdg12+3"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgextwlist
        package = "1.20-1.pgdg13+3"
      }
    }
  }
}
