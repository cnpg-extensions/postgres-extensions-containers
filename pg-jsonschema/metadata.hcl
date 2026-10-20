# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  build_system             = "pgrx"
  name                     = "pg-jsonschema"
  sql_name                 = "pg_jsonschema"
  image_name               = "pg-jsonschema"
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

  // The source release is declared in pg-jsonschema/Dockerfile. Keep the
  // catalog/image version synchronized with its Renovate tag comment.
  versions = {
    bookworm = {
      "18" = {
        package = "v0.3.4"
        sql     = "0.3.4"
      }
    }
    trixie = {
      "18" = {
        # renovate: datasource=github-tags depName=supabase/pg_jsonschema versioning=semver
        package = "v0.3.4"
        sql     = "0.3.4"
      }
    }
  }
}
