# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                       = "pgnodemx"
  sql_name                   = "pgnodemx"
  image_name                 = "pgnodemx"
  licenses                   = ["PostgreSQL", "Apache-2.0"]
  shared_preload_libraries   = ["pgnodemx"]
  postgresql_parameters      = {"pgnodemx.kdapi_enabled" = "off"}
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgnodemx
        package = "2.0.1-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgnodemx extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
        sql = "2.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgnodemx
        package = "2.0.1-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgnodemx extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
        sql = "2.0"
      }
    }
  }
}
