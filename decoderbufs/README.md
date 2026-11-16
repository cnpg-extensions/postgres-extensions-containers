# decoderbufs

A logical decoding output plugin that serializes change events as Protocol Buffers.
[Upstream project](https://github.com/debezium/postgres-decoderbufs).

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

PostgreSQL 18 on Debian Trixie and Bookworm, with amd64 and arm64 build targets.
### 1. Add the decoderbufs extension image to your Cluster

Use this declarative Cluster setup:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-decoderbufs
spec:
  imageCatalogRef: ...
  postgresql:
    parameters:
      wal_level: logical
      output_plugin_libraries: pgoutput,test_decoding,decoderbufs
    extensions:
    - name: decoderbufs
```

`decoderbufs` is an output plugin. Although the package contains a control file,
there is no SQL installation script: do not request `CREATE EXTENSION decoderbufs`
or list it in a Database resource's SQL extensions.

### 2. Verify operation

Clients connect through the CNPG-managed PostgreSQL Service, using a replication
role and approved authentication. Create a slot using the replication protocol
or an authorized SQL connection:

```sql
SELECT * FROM pg_create_logical_replication_slot('application_changes', 'decoderbufs');
```

Consume the slot with a compatible client that decodes decoderbufs protobuf
messages. Tables need suitable replica identity for UPDATE and DELETE.

Unconsumed replication slots retain WAL on the database's data volume. Monitor
consumer lag and disk use, configure an appropriate `max_slot_wal_keep_size`, and
drop unused slots with `pg_drop_replication_slot` after coordinating with their
consumers. No separate incoming listener or manual container setup is required.

## Dependencies, licenses and updates

The version-pinned PGDG `postgresql-18-decoderbufs` package supplies the plugin.
Package copyright notices are under `/licenses`. The matching `libprotobuf-c1`
runtime is bundled in `/system`; the base supplies libc. Generated protobuf
serialization code follows the decoderbufs package's update lifecycle;
protobuf-c is dynamically linked and updated separately.

Renovate tracks the PGDG package pin. Rebuild for protobuf-c or base-runtime
security updates and repeat architecture builds.
