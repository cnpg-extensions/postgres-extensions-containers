# decoderbufs

Serializes PostgreSQL change events as Protocol Buffers for logical replication
clients. Use it with a compatible CDC (change-data capture) client to send
record changes to another system.

For more information, see the [upstream documentation](https://github.com/debezium/postgres-decoderbufs).

### 1. Add the decoderbufs extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

Logical decoding requires `wal_level: logical` and `decoderbufs` in
`output_plugin_libraries`, as shown below.

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

### 2. Verify installation

`decoderbufs` does not appear in the database's installed-extension list
(`\dx` in `psql`).

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
