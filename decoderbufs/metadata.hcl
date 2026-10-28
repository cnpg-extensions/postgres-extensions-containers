# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "decoderbufs"
  sql_name                 = "decoderbufs"
  image_name               = "decoderbufs"
  licenses                 = ["MIT"]
  shared_preload_libraries = []
  postgresql_parameters    = {
    "output_plugin_libraries" = "pgoutput,test_decoding,decoderbufs"
    "wal_level" = "logical"
  }
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = false
  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-decoderbufs
        package = "3.7.0-1.pgdg12+1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-decoderbufs
        package = "3.7.0-1.pgdg13+1"
      }
    }
  }
}
