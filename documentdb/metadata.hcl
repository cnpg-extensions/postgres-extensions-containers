# SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "documentdb"
  sql_name                 = "documentdb"
  image_name               = "documentdb"
  licenses                 = ["MIT", "Apache-2.0", "PostgreSQL"]
  shared_preload_libraries = ["pg_cron", "pg_documentdb_core", "pg_documentdb", "pg_documentdb_extended_rum"]
  postgresql_parameters    = { "cron.database_name" = "app", "documentdb.localhost_connection_string" = "host=/controller/run" }
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["lib"]
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = ["pg-cron", "base-image:tsm_system_rows", "pgvector", "postgis", "rum", "base-image:documentdb_core"]
  create_extension         = true

  versions = {
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-documentdb
        package = "1.2-0-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-documentdb extractVersion=^(?<version>\d+\.\d+-\d+)
        sql     = "1.2-0"
      }
    }
  }
}
