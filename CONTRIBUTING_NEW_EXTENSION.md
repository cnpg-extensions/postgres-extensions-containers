# Requesting and adding extensions

## Start with an issue

[Request an extension](https://github.com/cnpg-extensions/postgres-extensions-containers/issues/new/choose)
with its name, upstream project link, and your use case. Share packaging and
license details if known. You do not need to investigate packaging, build an
image, or submit a PR first.

Maintainers maintain accepted extensions. Contributions are welcome, but
requesting an extension does not commit you to implementing or maintaining it.

## What we accept

**Debian packaging comes first.** It serves the wider PostgreSQL community and
helps resolve licensing, security, and dependency requirements. A missing package
alone is not a reason to build from source.

| Build path | When it applies |
| --- | --- |
| Debian | PGDG packages in `main`, available for both current Debian `stable` and `oldstable`. Other APT repositories or standalone `.deb` files do not qualify. |
| PGRX | PGRX extensions covered by the shared Rust toolchain exception. |
| Universe | Other extensions with documented dependency-packaging or delivery obstacles. |

See the [inclusion policy](source-build/README.md#inclusion-policy-debian-packaging-first)
for the rationale and source-build criteria.

All shipped material must meet the
[licensing policy](source-build/README.md#open-source-licensing-policy), including
notices, attribution, source availability, and redistribution obligations.
Build-only dependencies are outside its scope. Exceptions require explicit
approval and documentation.

Use the issue to settle eligibility, licensing concerns, and the build path
before substantial implementation work.

## Implementing an accepted proposal

This section is for maintainers, contributors, and coding agents doing the work.
Follow the general
[contribution guide](https://github.com/cloudnative-pg/governance/blob/main/CONTRIBUTING.md).

### Choose the recipe instructions

Fork this repository and create a branch for the extension. Follow the guide
for its build path:

- **Debian:** Use the [build guide](BUILD.md) and run
  `task create-extension NAME=<extension-name>`. Complete the generated
  `metadata.hcl`, `Dockerfile`, and `README.md`.
- **PGRX:** Use the [PGRX recipe guide](source-build/pgrx/README.md).
- **Universe:** Use the [Universe recipe guide](source-build/universe/README.md).

Source builds use their family templates. See [advanced scaffolding](BUILD.md#advanced-scaffolding)
for custom Debian versions or distributions.

### Record what will ship

Confirm the package or source version, shipped files, dependencies, and license
evidence. Add findings relevant to eligibility or packaging to the issue.

For Debian, inspect packages in disposable containers for both supported Debian
releases. Use `apt search`, install the package, and inspect it with `dpkg -L`.
Record the full package version, including its distribution suffix, such as
`0.8.2-1.pgdg13+1` or `0.8.2-1.pgdg12+1`.

Set metadata from the actual payload:

- `package`: full Debian package version, or literal upstream tag for source builds.
- `sql`: SQL extension version matching the control file's `default_version`.
  Required when `create_extension = true`.
- `create_extension`: set to `false` for modules without a `.control` file.

Preserve Renovate annotations. Verify the package-to-SQL-version mapping before
enabling automatic updates; follow the [update policy](README.md#automated-dependency-updates).

### Demonstrate that it works

Run the targeted checks and full local E2E test:

```sh
task prereqs
task checks TARGET="<extension-name>"
task e2e:test:full TARGET="<extension-name>"
```

PGRX and Universe require a native builder and pinned `sbom_generator`;
follow [builder setup](BUILD.md#usage-and-targets) and pass `BUILDER=<name>`
to the E2E task.

The E2E task builds the image, pushes it to a local registry, and tests it in Kind.
Check every expected PostgreSQL/distribution combination. Add extension-specific
Chainsaw tests in `test/` where useful.

Write and test README examples for `Cluster` and `Database` resources. In Kind,
use the local image reference:

```yaml
image:
  reference: registry.pg-extensions:5000/<extension-name>-testing:<tag>
```

The [local testing guide](BUILD.md#local-testing-guide) covers manual validation.
Clean up with `task e2e:cleanup`.

### Submit the result

Open a PR against this repository's `main` branch using the
[new-extension template](https://github.com/cnpg-extensions/postgres-extensions-containers/compare?expand=1&template=new_extension.md).
Include:

- A link to the proposal and a completed template checklist.
- The recipe, tested README examples, and any extension-specific tests.
- A `repository.release.distribution-points` entry in
  [SECURITY-INSIGHTS.yml](SECURITY-INSIGHTS.yml) for the image's GitHub Packages page,
  using `image_name` from metadata.
- Validation results stating what ran and what remains unverified.

Squash experimental commits. Use ``feat: add `<extension-name>` container image``
as the commit subject and reference the issue with `Closes #<issue-id>`.
Sign off every commit with `git commit -s`. AI-assisted commits also require an
`Assisted-By` trailer naming the assistant and model.
