# decoderbufs

A logical decoding output plugin that serializes change events as Protocol Buffers.
[Upstream project](https://github.com/debezium/postgres-decoderbufs).

## Supported images and setup

PostgreSQL 18 on Debian Trixie and Bookworm, with amd64 and arm64 build targets.
Use this declarative Cluster setup:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-decoderbufs
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1
  storage:
    size: 1Gi
  postgresql:
    parameters:
      wal_level: logical
      output_plugin_libraries: pgoutput,test_decoding,decoderbufs
    extensions:
    - name: decoderbufs
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-decoderbufs
        reference: ghcr.io/cnpg-extensions/decoderbufs:3.7.0-18-trixie
      ld_library_path: [system]
```

`decoderbufs` is an output plugin. Although the package contains a control file,
there is no SQL installation script: do not request `CREATE EXTENSION decoderbufs`
or list it in a Database resource's SQL extensions.

## Operation and verification

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

Maintained by Jeremy Schneider (@ardentperf).
