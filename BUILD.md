# Building Postgres Extensions Container Images for CloudNativePG

This guide explains how to build Postgres extensions container images for
[CloudNativePG](https://cloudnative-pg.io) locally, using
[Docker Bake](https://docs.docker.com/build/bake/).

> [!IMPORTANT]
> If you are looking to contribute a new PostgreSQL extension to this
> repository, please refer to the [`CONTRIBUTING_NEW_EXTENSION.md` file](CONTRIBUTING_NEW_EXTENSION.md).
> That contribution guide covers the entire lifecycle, from proposing the extension and
> scaffolding the project to local validation and submitting a Pull Request.

## Prerequisites

Before you begin, ensure that you have met the following
[prerequisites](https://github.com/cloudnative-pg/postgres-containers/blob/main/BUILD.md#prerequisites),
which primarily include:


1. **[Task](https://taskfile.dev/):** required to run tasks defined in the `Taskfile`.
2. **[Dagger](https://dagger.io/):** Must be installed and configured.
3. **Docker:** Must be installed and running.
4. **Docker Command Line:** The `docker` command must be executable.
5. **Docker Buildx:** The `docker buildx` plugin must be available.
6. **Docker Context:** A valid Docker context must be configured.

To verify that all prerequisites are correctly installed and configured:

```bash
task prereqs
```

---

## Scaffolding a New Extension

To create a new extension project structure, use the `create-extension` task:

```bash
task create-extension NAME=<extension-name>
```

This command generates a new directory named after your extension with the
following scaffolded files:

- `Dockerfile`: The base file to build the extension container image.
- `metadata.hcl`: Provides specific metadata information used to build and test
  the extension.
- `README.md`: A template to help you document the extension's usage.

> [!NOTE]
> These files are generated from generic templates and should be customized to
> meet your extension's specific requirements.
> For a complete walkthrough of the requirements and package discovery phase,
> see [`CONTRIBUTING_NEW_EXTENSION.md`](./CONTRIBUTING_NEW_EXTENSION.md).

For Universe source builds, use the [source-build templates](source-build/universe/README.md).
For Rust extensions, follow the [PGRX template guide](source-build/pgrx/README.md).

### Advanced Scaffolding

For more complex setups, you can use the `dagger` command directly to customize
distributions or package names:

```bash
dagger call -sm ./dagger/maintenance/ create --name="<name>" [ARGUMENTS] \
  export --path ./<name>
```

**Common Arguments:**

| Argument | Description | Default |
| --- | --- | --- |
| `--distros` | Debian distributions the extension supports (comma separated list). | `[trixie, bookworm]` |
| `--package-name` | The Debian package name (uses `%version%` placeholder). | `postgresql-%version%-<name>` |
| `--versions` | Supported Postgres major versions (comma separated list). | `[18]` |
| `--templates-dir` | Source directory containing custom template files. | Internal template dir |

---

## Usage and Targets

On `main`, automatic builds select changed extension payloads, including version
pins and system-library manifests. Documentation, tests, and shared build inputs
do not trigger production rebuilds. Shared changes take effect on the next build.

On non-main branches, shared CI, Dagger, packaging, and test changes select this
sample for the existing build, security, and integration checks:

- `pgtap`: SQL-only extension.
- `pg-cron`: native library and shared preload.
- `powa`: extensions supplied by the PostgreSQL base image.
- `mobilitydb`: upstream PostGIS dependency.
- `pltcl`: bundled OS libraries, data files, and environment paths.
- `pg-durable` (PGRX): standard Rust packaging and background-worker extension.
- `pg-session-jwt` (PGRX): Rust install path and guarded upstream lockfile correction.

The Debian workflow selects its sample; the shared source workflow selects the
PGRX sample and all discovered Universe recipes. Family-specific source tooling
changes select only that family's sample. Required gates report on every PR and
merge-queue commit, including empty build selections.

Direct payload changes always select their extension; changes
to extension-specific tests select that extension on branches only. Mixed shared
and extension changes test the union, without duplicate builds.

To build, test, and publish every extension using the latest merged inputs:

```bash
gh workflow run bake.yml --repo cnpg-extensions/postgres-extensions-containers \
  --ref main -f extension_name=all
gh workflow run source-build.yml --repo cnpg-extensions/postgres-extensions-containers \
  --ref main -f extension_name=all
```

Use a logical extension name (for example, `pg-duckdb`) instead of `all` to
rebuild one extension. Dispatching on another branch builds and tests without
copying images to production.

### 1. Build configuration check (dry run)

To verify the configuration (running `docker buildx bake --check`) for all
Debian recipes without executing their build steps:

```bash
task checks:all
```

### 2. Build all Debian recipes

To build all discovered Debian recipes:

```bash
task
# or
task bake:all
```

### 3. Build a specific project

To build a single project (e.g., the directory named `pg-cron`):

```bash
task bake TARGET=pg-cron
```

### 4. Push all Debian images

To build all Debian images and immediately push them to the configured registry:

```bash
task bake:all PUSH=true
```

### 5. Push images for a specific project

To push images for a single project (e.g., the directory named `pg-cron`):

```bash
task bake TARGET=pg-cron PUSH=true
```

### 6. Dry run mode

To see the commands that would be executed without running the actual
`docker buildx bake` command, set the `DRY_RUN` flag:

```bash
task DRY_RUN=true
# or
task bake TARGET=pg-cron DRY_RUN=true
```

The `:all` tasks discover Debian recipes only. For PGRX and Universe, use
`task checks TARGET=<name>` and `task bake TARGET=<name>` individually. Source
bakes require a native Docker-container builder via `BUILDER=<name>` and the
digest-qualified generator image in the lowercase `sbom_generator` environment
variable. See [source-build setup](source-build/README.md#local-builds).

## Local testing guide

Testing your extensions locally ensures high-quality PRs and faster iteration
cycles. This environment uses a local Docker container registry and a Kind
cluster with CloudNativePG pre-installed.

> [!IMPORTANT]
> **Pre-submission requirement:** You must successfully run local tests before
> submitting a Pull Request for any extension.

### The Fast Path (Automated Testing)

End-to-end (E2E) tests are powered by [Chainsaw](https://github.com/kyverno/chainsaw).
To simplify the workflow, use the `e2e:test:full` task.
This single command automates environment setup, image building, and test
execution:

```bash
# Replace <extension> with the name of the extension (e.g., pg-cron)
task e2e:test:full TARGET="<extension>"
```

The task tests PostgreSQL 19 on trixie by default. Set `PG_MAJOR` and
`DISTRO` to select another combination supported by the recipe.

For source recipes, also supply `BUILDER=<name>` and export `sbom_generator`
as described above.

Example for testing the `pg-cron` extension:

```bash
task e2e:test:full TARGET="pg-cron" PG_MAJOR=18
```

**When to use the step-by-step guide:** If the automated test fails during
environment setup, image building, or test execution, the step-by-step guide
below provides granular control for debugging each phase independently.

---

## E2E step-by-step Guide

### Initialize the environment

The `e2e:setup-env` utility creates a Kind cluster and attaches a local Docker
registry (available at `localhost:5000`).

```bash
task e2e:setup-env
```

> [!NOTE]
> Use the `REGISTRY_HOST_PORT` variable to customize the local registry port.
> If changed, you must pass this variable to all subsequent tasks that interact
> with the registry to ensure connectivity.

#### Configuring credentials for private registries

If you need to pull images from a private registry during testing, you can
configure authentication credentials when setting up the environment:

```bash
REGISTRY_PASSWORD="your-password" task e2e:setup-env \
  REGISTRY_HOST="registry.example.com" \
  REGISTRY_USERNAME="your-username"
```

These credentials are configured at the kubelet level, allowing pods to pull
images from the private registry without requiring ImagePullSecrets.

### Get access to the cluster

To interact with the cluster via `kubectl` from your local terminal:

```bash
task e2e:export-kubeconfig KUBECONFIG_PATH=./kubeconfig
export KUBECONFIG=$PWD/kubeconfig
```

> [!IMPORTANT]
> The local registry running alongside the Kind cluster is
> reachable within Kubernetes at `registry.pg-extensions:5000`. When testing your
> local builds, you must point the extension's `reference` to this internal
> address.
> For example, if you are testing a locally built `pg-cron` image, use:
> `reference: registry.pg-extensions:5000/pg-cron-testing:<tag>`

To allow the test suite (which runs within the Docker network) to reach the
Kubernetes API server, export the internal Kubeconfig:

```bash
task e2e:export-kubeconfig KUBECONFIG_PATH=./kubeconfig INTERNAL=true
```

### Build and push the extension (`bake`)

Build the image and push it to the local registry. This command tags the image
for `localhost:5000` automatically.

```bash
task bake TARGET="<extension>" PUSH=true
```

> [!NOTE]
> The destination registry is controlled by the `REGISTRY_HOST_NAME` and
> `REGISTRY_HOST_PORT` variables defined in the `Taskfile.yml`.

### Prepare testing values

Generate configuration values so Chainsaw knows which local image to target for
the E2E tests:

```bash
task e2e:generate-values TARGET="<extension>" EXTENSION_IMAGE="<my-local-image>"
```

#### Using private registries

If your extension image is hosted in a private registry, you can provide authentication
credentials when generating test values:

```bash
REGISTRY_PASSWORD="your-password" task generate-values \
  TARGET="<extension>" \
  EXTENSION_IMAGE="<my-private-registry>/image:tag" \
  REGISTRY_USERNAME="your-username"
```

### Execute End-to-End tests

Run the test suite using the internal Kubeconfig. This executes both the
generic tests (global `/test` folder) and extension-specific tests (target
`/test` folder).

```bash
task e2e:test TARGET="<extension>" KUBECONFIG_PATH="./kubeconfig"
```

#### Pass arguments to chainsaw test

It is possible to pass arguments to the [Chainsaw test command](https://kyverno.github.io/chainsaw/latest/reference/commands/chainsaw_test/) by using the `EXTRA_ARGS` 
argument, like:

```bash
task e2e:test TARGET="pg-cron" KUBECONFIG_PATH="./kubeconfig" EXTRA_ARGS="--skip-delete,--fail-fast"
```

---

### Tear down the local test environment

To clean up all the resources created by the `e2e:setup-env` task, run:

```bash
task e2e:cleanup
```
