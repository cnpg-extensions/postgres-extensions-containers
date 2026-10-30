# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "ogr-fdw"
  sql_name                 = "ogr_fdw"
  image_name               = "ogr-fdw"
  licenses                 = ["MIT"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {
    "GDAL_DATA" = "$${image_root}/share/gdal"
    "PROJ_DATA" = "$${image_root}/share/proj"
  }
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-ogr-fdw
        package = "1.1.9-1.pgdg12+2"
        // The PGDG package version and extension catalog version are independent.
        // renovate: suite=bookworm-pgdg depName=postgresql-18-ogr-fdw extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
        sql     = "1.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-ogr-fdw
        package = "1.1.9-1.pgdg13+2"
        // The PGDG package version and extension catalog version are independent.
        // renovate: suite=trixie-pgdg depName=postgresql-18-ogr-fdw extractVersion=^(?:[0-9]+:)?(?<version>[0-9]+[.][0-9]+)
        sql     = "1.1"
      }
    }
  }
}
