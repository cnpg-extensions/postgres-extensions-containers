# DocumentDB end-to-end test record

The shared Chainsaw smoke test installs the extension and verifies its name and
version as the ordinary `app` login. Installation applies the planner schema grants.

On a separate two-instance CNPG Playground cluster, mongosh authenticated over
TLS, wrote and read a document, then read the same document and repeated the
write/read check after the replica became primary.

Run in Bash on the Docker host from the repository root, with kind,
kubectl (including the cnpg plugin), Helm, OpenSSL, Task, Dagger, psql and mongosh
available. The recorded client was Linux x86-64 mongosh 2.14.3.

## Shared smoke suite

```bash
task e2e:test:full TARGET=documentdb
```

## Gateway on CNPG Playground

Use a fresh Playground alongside the local registry created by the smoke suite.
The catalog below contains the four prerequisite images from the test fixture.
The manifest substitutes the digest of your local build.

```bash
umask 077
work=$(mktemp -d)
task bake TARGET=documentdb PUSH=true
digest=$(docker buildx imagetools inspect localhost:5000/documentdb-testing:1.2-18-trixie --format '{{.Manifest.Digest}}')
git clone https://github.com/cloudnative-pg/cnpg-playground "$work/playground"
git -C "$work/playground" checkout 2e2bbb7906e61d826dedd963a82aad81dce8d63b
export K8S_NAME=docdb-pin- RUSTFS_BASE_PORT=19232
(cd "$work/playground" && bash scripts/setup.sh pincase)
export KUBECONFIG="$work/playground/k8s/kube-config.yaml"
for node in $(kind get nodes --name docdb-pin-pincase); do
  docker network connect pg-extensions-e2e "$node"
  docker exec -i "$node" sh -c 'mkdir -p /etc/containerd/certs.d/registry.pg-extensions:5000 && cat > /etc/containerd/certs.d/registry.pg-extensions:5000/hosts.toml' <<'EOF'
server = "http://registry.pg-extensions:5000"
[host."http://registry.pg-extensions:5000"]
  capabilities = ["pull", "resolve"]
EOF
done
kubectl apply --server-side -f https://github.com/cert-manager/cert-manager/releases/download/v1.19.1/cert-manager.yaml
kubectl -n cert-manager rollout status deployment/cert-manager-webhook
kubectl apply --server-side -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.30/releases/cnpg-1.30.2.yaml
kubectl -n cnpg-system rollout status deployment/cnpg-controller-manager
helm template documentdb oci://ghcr.io/documentdb/documentdb-operator --version 1.2.0 \
  --set cloudnative-pg.enabled=false --api-versions cert-manager.io/v1/Certificate \
  --show-only templates/02_documentdb_sidecar_injector.yaml | kubectl apply -f -
kubectl -n cnpg-system rollout status deployment/sidecar-injector
kubectl apply -f - <<'EOF'
apiVersion: postgresql.cnpg.io/v1
kind: ClusterImageCatalog
metadata:
  name: postgresql-minimal-trixie
spec:
  images:
  - extensions:
    - image:
        reference: ghcr.io/cnpg-extensions/pg-cron:1.6.8-202611130420-18-trixie@sha256:1f3eec1740ffa0c2856bb652883f031813cccbfc26134b82ba770cb63169a190
      name: pg-cron
    - image:
        reference: ghcr.io/cloudnative-pg/pgvector:0.8.7-202611201143-18-trixie@sha256:8c719f4ba8796a39b1e08a450b424577be9fd9821089dfd2c90e8c2d86b7a03c
      name: pgvector
    - env:
      - name: GDAL_DATA
        value: ${image_root}/share/gdal
      - name: PROJ_DATA
        value: ${image_root}/share/proj
      image:
        reference: ghcr.io/cloudnative-pg/postgis-extension:3.7.0-202611201143-18-trixie@sha256:ea0a56f3182b9c4e9d4931657722c32473c0874cdf324b37b36e5f7be5a20cba
      ld_library_path:
      - system
      name: postgis
    - image:
        reference: ghcr.io/cnpg-extensions/rum:1.3.15-202611130708-18-trixie@sha256:824136a3d05767761fd0d53db1bce30921628b10d65f69b1850a1e097476abe4
      name: rum
    image: ghcr.io/cloudnative-pg/postgresql:18.7-202611160820-minimal-trixie@sha256:452a15584e2aa1ce658c4ae8538b5dc157eb031d41b82fd19882e0c03bcec01d
    major: 18
EOF
kubectl create namespace documentdb
openssl req -x509 -newkey rsa:2048 -nodes -days 3 -subj /CN=documentdb-test-ca \
  -keyout "$work/ca.key" -out "$work/ca.crt"
kubectl -n documentdb create secret tls test-ca --cert="$work/ca.crt" --key="$work/ca.key"
kubectl -n documentdb apply -f - <<'EOF'
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: documentdb-ca
spec:
  ca:
    secretName: test-ca
EOF
openssl rand -hex 24 | tr -d '\n' > "$work/password"
kubectl -n documentdb create secret generic mongo-admin --type=kubernetes.io/basic-auth \
  --from-literal=username=mongo_admin --from-file=password="$work/password"
kubectl -n documentdb apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: documentdb-credentials
stringData:
  username: ""
  password: ""
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: documentdb-gateway
spec:
  secretName: documentdb-gateway-tls
  issuerRef:
    name: documentdb-ca
  dnsNames:
  - documentdb-gateway
  - documentdb-gateway.documentdb.svc
---
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-documentdb
spec:
  instances: 2
  storage:
    size: 1Gi
  imageCatalogRef:
    apiGroup: postgresql.cnpg.io
    kind: ClusterImageCatalog
    name: postgresql-minimal-trixie
    major: 18
  bootstrap:
    initdb:
      postInitSQL:
      - CREATE EXTENSION pg_cron
      - CREATE EXTENSION tsm_system_rows
      - CREATE EXTENSION vector
      - CREATE EXTENSION postgis
      - CREATE EXTENSION rum WITH SCHEMA public
      - CREATE EXTENSION documentdb_core
      - CREATE EXTENSION documentdb
      - CREATE EXTENSION documentdb_extended_rum WITH SCHEMA public
      - CREATE ROLE documentdb_socket_users NOLOGIN
      - CREATE ROLE documentdb LOGIN
      - GRANT documentdb_admin_role TO documentdb
  postgresql:
    extensions:
    - name: pg-cron
    - name: pgvector
    - name: postgis
    - name: rum
    - name: documentdb
      ld_library_path: [lib]
      image:
        reference: registry.pg-extensions:5000/documentdb-testing:1.2-18-trixie@$digest
    shared_preload_libraries:
    - pg_cron
    - pg_documentdb_core
    - pg_documentdb
    - pg_documentdb_extended_rum
    parameters:
      cron.database_name: postgres
      documentdb.localhost_connection_string: host=/controller/run
    pg_ident:
    - local postgres +documentdb_socket_users
    pg_hba:
    - host postgres documentdb,+documentdb_socket_users 127.0.0.1/32 trust
    - host postgres documentdb,+documentdb_socket_users ::1/128 trust
  managed:
    roles:
    - name: mongo_admin
      login: true
      passwordSecret:
        name: mongo-admin
      inRoles:
      - documentdb_socket_users
      - documentdb_admin_role
  plugins:
  - name: cnpg-i-sidecar-injector.documentdb.io
    parameters:
      gatewayImage: ghcr.io/documentdb/documentdb-kubernetes-operator/gateway:1.0.1@sha256:502b4e7bfcbb926597a9f9d4a2a6dc8174ff502fbcf72cdb9e4c1a3b2d58a41e
      gatewayTLSSecret: documentdb-gateway-tls
---
apiVersion: v1
kind: Service
metadata:
  name: documentdb-gateway
spec:
  selector:
    cnpg.io/cluster: cluster-documentdb
    cnpg.io/instanceRole: primary
  ports:
  - name: mongodb
    port: 10260
EOF
kubectl -n documentdb wait --for=condition=Ready cluster/cluster-documentdb --timeout=10m
```

## Authenticate, write, and read after switchover

Keep this shell open. Enter the contents of `$work/password` at each mongosh
prompt. The host alias preserves TLS hostname verification through the port-forward.

```bash
echo 'documentdb-gateway localhost' > "$work/hosts-aliases"
export HOSTALIASES="$work/hosts-aliases"
gateway_shell() {
  mongosh 'mongodb://documentdb-gateway:10260/catalog?authSource=admin&directConnection=true' \
    --tls --tlsCAFile "$work/ca.crt" --username mongo_admin
}
forward_gateway() {
  kubectl -n documentdb port-forward svc/documentdb-gateway 10260:10260 > "$work/forward.log" 2>&1 &
  forward_pid=$!
  until grep -q 'Forwarding from' "$work/forward.log"; do
    kill -0 "$forward_pid" || return 1
    sleep 0.2
  done
}
forward_gateway && gateway_shell
```

```javascript
db.items.updateOne({ _id: "gateway-check" }, { $set: { ready: true } }, { upsert: true })
db.items.findOne({ _id: "gateway-check" })
exit
```

Expect an acknowledged write and a document containing `ready: true`. Switch
to the replica, wait for it to become primary, then reconnect through the Service.

```bash
kill "$forward_pid"
replica=$(kubectl -n documentdb get pods -l 'cnpg.io/cluster=cluster-documentdb,cnpg.io/instanceRole=replica' -o jsonpath='{.items[0].metadata.name}')
kubectl cnpg promote -n documentdb cluster-documentdb "$replica"
kubectl -n documentdb wait --for=jsonpath='{.status.currentPrimary}'="$replica" cluster/cluster-documentdb --timeout=5m
kubectl -n documentdb wait --for=condition=Ready cluster/cluster-documentdb --timeout=5m
forward_gateway && gateway_shell
```

Read before writing again. Expect the same document on the new primary.

```javascript
db.items.findOne({ _id: "gateway-check" })
db.items.updateOne({ _id: "gateway-check" }, { $set: { ready: true } }, { upsert: true })
db.items.findOne({ _id: "gateway-check" })
exit
```

```bash
kill "$forward_pid"
(cd "$work/playground" && bash scripts/teardown.sh pincase)
rm -f "$work/password" "$work/ca.key"
```
