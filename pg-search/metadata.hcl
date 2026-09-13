# SPDX-FileCopyrightText: Copyright © contributors to the Not-CloudNativePG project.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-search"
  sql_name                 = "pg_search"
  image_name               = "pg-search"
  licenses                 = ["AGPL-3.0-only"]
  shared_preload_libraries = ["pg_search"]
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = ["pgvector"]
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        package = "0.25.6"
        sql     = "0.25.6"
      }
    }
    trixie = {
      "18" = {
        package = "0.25.6"
        sql     = "0.25.6"
      }
    }
  }
}
