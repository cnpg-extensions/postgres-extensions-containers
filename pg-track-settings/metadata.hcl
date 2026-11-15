# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                       = "pg-track-settings"
  sql_name                   = "pg_track_settings"
  image_name                 = "pg-track-settings"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-track-settings
        package = "2.1.2-5.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-track-settings extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+[.][0-9]+)
        sql = "2.1.2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-track-settings
        package = "2.1.2-5.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-track-settings extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+[.][0-9]+)
        sql = "2.1.2"
      }
    }
  }
}
