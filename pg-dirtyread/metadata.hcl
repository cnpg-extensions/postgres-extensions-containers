# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                       = "pg-dirtyread"
  sql_name                   = "pg_dirtyread"
  image_name                 = "pg-dirtyread"
  licenses                   = ["BSD-3-Clause"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-dirtyread
        package = "2.8-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-dirtyread extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+)
        sql = "2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-dirtyread
        package = "2.8-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-dirtyread extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+)
        sql = "2"
      }
    }
  }
}
