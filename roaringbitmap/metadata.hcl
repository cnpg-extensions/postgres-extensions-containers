# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "roaringbitmap"
  sql_name                 = "roaringbitmap"
  image_name               = "roaringbitmap"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-roaringbitmap
        package = "1.3.0~rc1-1.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-roaringbitmap extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.3"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-roaringbitmap
        package = "1.3.0~rc1-1.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-roaringbitmap extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.3"
      }
    }
  }
}
