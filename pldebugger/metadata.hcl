# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pldebugger"
  sql_name                 = "pldbgapi"
  image_name               = "pldebugger"
  licenses                 = ["Artistic-2.0"]
  shared_preload_libraries = ["plugin_debugger"]
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pldebugger
        package = "1:1.10-1.pgdg12+1"
        // SQL version cannot be updated by Renovate; if it changes, manually update pldebugger/README.md, pldebugger/metadata.hcl, and renovate.json.
        sql     = "1.1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pldebugger
        package = "1:1.10-1.pgdg13+1"
        // SQL version cannot be updated by Renovate; if it changes, manually update pldebugger/README.md, pldebugger/metadata.hcl, and renovate.json.
        sql     = "1.1"
      }
    }
  }
}
