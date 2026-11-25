# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  build_system             = "pgrx"
  name                     = "pg-parquet"
  sql_name                 = "pg_parquet"
  image_name               = "pg-parquet"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_parquet"]
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
        # renovate: datasource=github-tags depName=CrunchyData/pg_parquet versioning=semver
        package = "v0.6.2"
        sql     = "0.6.2"
      }
      "19" = {
        # renovate: datasource=github-tags depName=CrunchyData/pg_parquet versioning=semver
        package = "v0.6.2"
        sql     = "0.6.2"
      }
    }
    trixie = {
      "18" = {
        # renovate: datasource=github-tags depName=CrunchyData/pg_parquet versioning=semver
        package = "v0.6.2"
        sql     = "0.6.2"
      }
      "19" = {
        # renovate: datasource=github-tags depName=CrunchyData/pg_parquet versioning=semver
        package = "v0.6.2"
        sql     = "0.6.2"
      }
    }
  }
}
