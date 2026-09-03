# PostGIS (stub)
<!--
SPDX-FileCopyrightText: Copyright © contributors to CNPG Extensions.
SPDX-License-Identifier: Apache-2.0
-->

PostGIS is maintained upstream at
[cloudnative-pg/postgres-extensions-containers](https://github.com/cloudnative-pg/postgres-extensions-containers)
and its images are published at `ghcr.io/cloudnative-pg/postgis-extension`.

This stub directory exists so that extensions in this fork with
`required_extensions = ["postgis"]` (such as `mobilitydb`) can be tested
against the upstream published PostGIS image.

For production use, use the upstream PostGIS extension image:
`ghcr.io/cloudnative-pg/postgis-extension`
