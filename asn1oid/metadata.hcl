# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "asn1oid"
  sql_name                 = "asn1oid"
  image_name               = "asn1oid"
  licenses                 = ["GPL-3.0-or-later"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-asn1oid
        package = "1.6-3.pgdg12+2"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-asn1oid extractVersion=^(?<version>\d+)
        sql     = "1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-asn1oid
        package = "1.6-3.pgdg13+2"
        // renovate: suite=trixie-pgdg depName=postgresql-18-asn1oid extractVersion=^(?<version>\d+)
        sql     = "1"
      }
    }
  }
}
