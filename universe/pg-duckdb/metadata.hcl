# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-duckdb"
  sql_name                 = "pg_duckdb"
  image_name               = "pg-duckdb"
  licenses                 = ["MIT"]

  shared_preload_libraries = ["pg_duckdb"]
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        # renovate: datasource=github-releases depName=duckdb/pg_duckdb versioning=semver
        package = "v1.2.2"
        sql     = "1.2.2"
      }
    }
    trixie = {
      "18" = {
        # renovate: datasource=github-releases depName=duckdb/pg_duckdb versioning=semver
        package = "v1.2.2"
        sql     = "1.2.2"
      }
    }
  }
}
