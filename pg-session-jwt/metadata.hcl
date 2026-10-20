# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  build_system             = "pgrx"
  name                     = "pg-session-jwt"
  sql_name                 = "pg_session_jwt"
  image_name               = "pg-session-jwt"
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
    bookworm = {
      "18" = {
        # renovate: datasource=github-tags depName=neondatabase/pg_session_jwt versioning=semver
        package = "v0.5.0"
        sql     = "0.5.0"
      }
    }
    trixie = {
      "18" = {
        # renovate: datasource=github-tags depName=neondatabase/pg_session_jwt versioning=semver
        package = "v0.5.0"
        sql     = "0.5.0"
      }
    }
  }
}
