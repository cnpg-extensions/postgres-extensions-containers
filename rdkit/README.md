# RDKit PostgreSQL cartridge

RDKit provides cheminformatics types and functions in PostgreSQL, including SMILES parsing, molecule fingerprints and molecular descriptors. See the [upstream RDKit project](https://github.com/rdkit/rdkit) for toolkit documentation.

The PG18 package is available on Trixie only in this matrix, for amd64 and arm64. Bookworm has RDKit packages for older PostgreSQL majors but no PG18 package.

Follow the [quick start](../README.md#quick-start) to set up extension-update email
alerts first, then install the catalog and enable weekly maintenance. These examples
inherit image references and runtime settings from the catalog. The Cluster YAML
is an excerpt: replace `imageCatalogRef: ...` with your catalog reference and
keep your existing instance and storage settings.

## Usage

### 1. Add the rdkit extension image to your Cluster

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

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

Connect to the database with `psql` and run `\dx` to check the installed extensions.

Parse a molecular SMILES string, canonicalize it and generate a Morgan fingerprint:

~~~sql
SELECT mol_to_smiles(mol_from_smiles('CCO'))::text = 'CCO'
   AND size(morganbv_fp(mol_from_smiles('CCO'))) > 0;
~~~

No writable storage or runtime shell access is needed for the SQL cartridge functions shown here.

## Package, licensing and updates

PGDG package: 202503.1-5.pgdg13+1; SQL version: 4.7.0. RDKit is BSD-3-Clause; its package copyright and notices for bundled runtime dependencies are included under `/licenses/<package>/`. The image includes no source archives.

Renovate tracks the PGDG package. Rebuild after package or base-image security updates and review the resulting runtime libraries and their notices.
