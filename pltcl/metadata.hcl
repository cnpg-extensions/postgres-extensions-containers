# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pltcl"
  sql_name                 = "pltcl"
  image_name               = "pltcl"
  licenses                 = ["PostgreSQL", "TCL"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {
    "TCL_LIBRARY"    = "$${image_root}/share/tcl8.6"
    "TCL8_6_TM_PATH" = "$${image_root}/share/tcl8.6/tcl8"
  }
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-pltcl-18
        package = "18.7-1.pgdg12+2"
        // SQL version is independent of the package version; inspect control files before merging.
        sql     = "1.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-pltcl-18
        package = "18.7-1.pgdg13+2"
        // SQL version is independent of the package version; inspect control files before merging.
        sql     = "1.0"
      }
    }
  }
}
