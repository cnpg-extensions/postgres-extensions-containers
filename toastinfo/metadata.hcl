# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "toastinfo"
  sql_name                 = "toastinfo"
  image_name               = "toastinfo"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-toastinfo
        package = "1.7-1.pgdg12+2"
        // toastinfo's SQL extension version is independent of its package version.
        sql     = "1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-toastinfo
        package = "1.7-1.pgdg13+2"
        // toastinfo's SQL extension version is independent of its package version.
        sql     = "1"
      }
    }
  }
}
