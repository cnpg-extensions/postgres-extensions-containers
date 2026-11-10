# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  build_system             = "pgrx"
  source_repository        = "https://github.com/pmpetit/pglinter"
  name                     = "pglinter"
  sql_name                 = "pglinter"
  image_name               = "pglinter"
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

  // The Dockerfile lockfile workaround must be manually reviewed on update.
  versions = {
    bookworm = {
      "18" = {
        # renovate: datasource=github-tags depName=pmpetit/pglinter versioning=semver
        package = "2.0.0"
        sql     = "2.0.0"
      }
    }
    trixie = {
      "18" = {
        # renovate: datasource=github-tags depName=pmpetit/pglinter versioning=semver
        package = "2.0.0"
        sql     = "2.0.0"
      }
    }
  }
}
