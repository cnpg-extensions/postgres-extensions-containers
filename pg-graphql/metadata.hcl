# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  build_system             = "pgrx"
  name                     = "pg-graphql"
  sql_name                 = "pg_graphql"

  image_name               = "pg-graphql"

  licenses                 = ["Apache-2.0"]

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
    trixie = {
      "18" = {
        # renovate: datasource=github-tags depName=supabase/pg_graphql versioning=semver
        package = "v1.6.2"
        sql     = "1.6.2"
      }
    }
    bookworm = {
      "18" = {
        # renovate: datasource=github-tags depName=supabase/pg_graphql versioning=semver
        package = "v1.6.2"
        sql     = "1.6.2"
      }
    }
  }
}
