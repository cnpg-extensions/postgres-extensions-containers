# RDKit PostgreSQL cartridge

Provides cheminformatics types and functions in PostgreSQL, including SMILES
parsing, molecule fingerprints and molecular descriptors. Use it to find
molecules that resemble a known chemical or contain a particular structure.

For more information, see the [upstream documentation](https://github.com/rdkit/rdkit).

### 1. Add the rdkit extension image to your Cluster

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-rdkit
spec:
  imageCatalogRef: ...
  postgresql:
    extensions:
    - name: rdkit
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION rdkit;` in the target database.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Parse a molecular SMILES string, canonicalize it and generate a Morgan fingerprint:

~~~sql
SELECT mol_to_smiles(mol_from_smiles('CCO'))::text = 'CCO'
   AND size(morganbv_fp(mol_from_smiles('CCO'))) > 0;
~~~

No writable storage or runtime shell access is needed for the SQL cartridge functions shown here.

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
