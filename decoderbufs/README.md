# decoderbufs

[decoderbufs](https://github.com/debezium/postgres-decoderbufs) serializes PostgreSQL change events as Protocol Buffers for logical
replication clients.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your instance and storage settings, following any extension-specific
requirements below.

## Usage

For more information, see the [upstream documentation](https://github.com/debezium/postgres-decoderbufs).

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

### 2. Verify installation

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

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
