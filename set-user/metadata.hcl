# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                       = "set-user"
  sql_name                   = "set_user"
  image_name                 = "set-user"
  licenses                   = ["PostgreSQL"]
  shared_preload_libraries   = ["set_user"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-set-user
        package = "4.3.0-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-set-user extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+[.][0-9]+)
        sql = "4.3.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-set-user
        package = "4.3.0-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-set-user extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+[.][0-9]+)
        sql = "4.3.0"
      }
    }
  }
}
