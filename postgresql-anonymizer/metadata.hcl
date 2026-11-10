# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  build_system             = "pgrx"
  source_repository        = "https://gitlab.com/dalibo/postgresql_anonymizer"
  name                     = "postgresql-anonymizer"
  sql_name                 = "anon"
  image_name               = "postgresql-anonymizer"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["anon"]
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
        # renovate: datasource=gitlab-tags depName=dalibo/postgresql_anonymizer versioning=semver
        package = "3.3.2"
        sql     = "3.3.2"
      }
    }
    trixie = {
      "18" = {
        # renovate: datasource=gitlab-tags depName=dalibo/postgresql_anonymizer versioning=semver
        package = "3.3.2"
        sql     = "3.3.2"
      }
    }
  }
}
