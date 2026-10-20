# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  build_system             = "pgrx"
  name                     = "pg-durable"
  sql_name                 = "pg_durable"

  image_name               = "pg-durable"

  licenses                 = ["PostgreSQL"]

  shared_preload_libraries = ["pg_durable"]
  postgresql_parameters    = { "pg_durable.database" = "app" }
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
        # renovate: datasource=github-tags depName=microsoft/pg_durable versioning=semver
        package = "v0.2.7"
        sql     = "0.2.7"
      }
    }
    trixie = {
      "18" = {
        # renovate: datasource=github-tags depName=microsoft/pg_durable versioning=semver
        package = "v0.2.7"
        sql     = "0.2.7"
      }
    }
  }
}
