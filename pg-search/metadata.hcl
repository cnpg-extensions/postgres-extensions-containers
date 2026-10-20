# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  build_system             = "pgrx"
  name                     = "pg-search"
  sql_name                 = "pg_search"
  image_name               = "pg-search"
  licenses                 = ["AGPL-3.0"]
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
        # renovate: datasource=github-tags depName=paradedb/paradedb versioning=semver
        package = "v0.25.6"
        sql     = "0.25.6"
      }
    }
    trixie = {
      "18" = {
        # renovate: datasource=github-tags depName=paradedb/paradedb versioning=semver
        package = "v0.25.6"
        sql     = "0.25.6"
      }
    }
  }
}
