# credcheck

Checks usernames and passwords against configurable policies when roles are
created or credentials change. Use it to stop database users from choosing
passwords that are too short or easy to guess.

Password complexity checks require setting passwords through SQL with the
plaintext password available to the database. This is incompatible with
`psql`'s `\password` command and CNPG declarative password management, which
submit precomputed hashes that credcheck rejects by default. Consider the
security implications of transmitting passwords to the database rather than
precomputed hashes, including how the connection is protected.

Follow the [quick start](../README.md#quick-start) to set up extension-update email alerts
first, then use the CronJob to install and refresh the catalog.

For more information, see the [upstream documentation](https://github.com/MigOpsRepos/credcheck).

### 1. Add the credcheck extension image to your Cluster

This extension requires `credcheck` in `shared_preload_libraries`, as shown
below.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-credcheck
spec:
  imageCatalogRef: ...
  postgresql:
    shared_preload_libraries:
    - credcheck
    extensions:
    - name: credcheck
```

### 2. Enable the extension in a database

Once the extension's files are available in the cluster, you can install it in a
database in either of two ways:

- **Declaratively**, using a [CloudNativePG `Database` resource](https://cloudnative-pg.io/docs/1.30/declarative_database_management/#managing-extensions-in-a-database).
- **Through SQL**, by running `CREATE EXTENSION credcheck;` in the target database.

Platform teams may make extension containers available across their clusters
without installing every extension in every database. Install only the extensions
a database uses; letting users enable them through SQL alongside the rest of their
DDL schema management code can be a convenient approach.

For extensions that normally require superuser privileges, platform teams can use
[pgextwlist](../pgextwlist/README.md) to allow non-superusers to install an
administrator-approved selection of extensions.

### 3. Verify installation

```sql
SELECT count(*) AS banned_roles FROM pg_banned_role;
```

## Licenses and Copyright

Extension and dependency licenses and copyright notices are bundled in
`/licenses/` in the image.
