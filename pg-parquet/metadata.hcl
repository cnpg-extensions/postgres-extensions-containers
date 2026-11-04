# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-parquet"
  sql_name                 = "pg_parquet"
  image_name               = "pg-parquet"
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

  // Built from the upstream release tag; `package` is the tag without the "v".
  // `sql` is the Cargo version (= default_version in pg_parquet.control) and must be bumped manually.
  versions = {
    bookworm = {
      "18" = {
        // renovate: datasource=github-tags depName=CrunchyData/pg_parquet extractVersion=^v(?<version>.+)$
        package = "0.5.1"
        sql     = "0.5.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: datasource=github-tags depName=CrunchyData/pg_parquet extractVersion=^v(?<version>.+)$
        package = "0.5.1"
        sql     = "0.5.1"
      }
    }
  }
}
