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

  // Built from the upstream release tag; `package` is the tag without the "v".
  // `sql` is the default_version in pg_duckdb.control and must be bumped manually.
  versions = {
    bookworm = {
      "18" = {
        // renovate: datasource=github-tags depName=duckdb/pg_duckdb extractVersion=^v(?<version>.+)$
        package = "1.1.1"
        sql     = "1.1.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: datasource=github-tags depName=duckdb/pg_duckdb extractVersion=^v(?<version>.+)$
        package = "1.1.1"
        sql     = "1.1.0"
      }
    }
  }
}
