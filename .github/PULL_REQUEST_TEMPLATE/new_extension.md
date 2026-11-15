<!--
Thanks for contributing a new extension to the PostgreSQL Extensions Containers
project!

Before opening this PR, please make sure you have read:
  - CONTRIBUTING_NEW_EXTENSION.md (lifecycle for adding an extension)
  - BUILD.md (build system)
  - the general CloudNativePG CONTRIBUTING.md:
    https://github.com/cloudnative-pg/governance/blob/main/CONTRIBUTING.md
-->

## Extension

<!-- Name of the extension and a short description of what it does and its
     primary use case. -->



Closes #<!-- proposal issue id -->

---

## Contributor checklist

<!-- All items must be addressed before requesting a review. -->

- [ ] My commits are signed off for [DCO](https://developercertificate.org/)
      compliance (`git commit -s`).
- [ ] Experimental commits have been squashed into a single, well-formed commit.
- [ ] This PR targets the `main` branch of the CNPG Extensions repository.
- [ ] A [New Extension Proposal](https://github.com/cnpg-extensions/postgres-extensions-containers/issues/new/choose)
      issue exists and is referenced via `Closes #<id>` above.
- [ ] The commit message follows the format:
      ``feat: add `<extension-name>` container image``.
- [ ] For a Debian recipe, the package was verified in `main` on both Debian
      `stable` (`trixie`) and `oldstable` (`bookworm`),
      or the proposal documents the reason for a PGRX/Universe source build.
- [ ] The extension follows its family templates (Debian, PGRX or Universe),
      and all generated `TODO` comments were resolved.
- [ ] `metadata.hcl` sets the correct `package` (full Debian version or literal source tag) and, when
      `create_extension = true`, the matching `sql` (catalog) version.
- [ ] `create_extension` is set correctly (`false` for PostgreSQL *modules* with
      no `.control` file, verified in the package or source installation).
- [ ] Renovate annotations and rules match the recipe family and upstream
      version scheme, with a verified package-to-SQL-version mapping.
- [ ] Every distributed component meets the
      [Open Source Licensing Policy](https://github.com/cnpg-extensions/postgres-extensions-containers#open-source-licensing-policy),
      with any exceptions explicitly approved and documented;
      SPDX `licenses` in `metadata.hcl` are accurate.
- [ ] `task checks TARGET="<extension-name>"` passes locally.
- [ ] Full E2E passes: `task e2e:test:full TARGET="<extension-name>"`.
- [ ] `README.md` is complete and includes a working `Cluster` example (plus a
      `Database` example with `CREATE EXTENSION` when `create_extension = true`).
- [ ] A `distribution-points` entry for the new image was added under
      `repository.release` in
      [`SECURITY-INSIGHTS.yml`](https://github.com/cnpg-extensions/postgres-extensions-containers/blob/main/SECURITY-INSIGHTS.yml).

---

## Maintainer review checklist

<!-- For maintainers only. Do not merge until every item is verified. -->

- [ ] The linked proposal issue is approved (label `new-extension`) and the
      `Closes #<id>` reference is correct.
- [ ] CI is green: the applicable Debian or shared source-build workflow built
      the new target for the full
      `pgVersions × distributions × {amd64, arm64}` matrix.
- [ ] DCO check passes and history is a single clean commit with the required
      `feat: add ...` message format.
- [ ] License compliance reviewed: all distributed components, including bundled
      data, meet the Open Source Licensing Policy or have an explicitly approved
      and documented exception. Applicable notices, attribution, source availability
      and redistribution obligations are satisfied; SPDX `licenses` match.
- [ ] `metadata.hcl` reviewed: `package`/`sql` versions, `create_extension`,
      runtime settings (`shared_preload_libraries`, `*_path`, `env`,
      `required_extensions`) and behavior flags are correct.
- [ ] Renovate annotations and rules are correct so automated version PRs track
      the package going forward.
- [ ] `Dockerfile` reviewed: final stage is `FROM scratch` and contains only the
      expected artifacts; the `USER 65532:65532` directive matches the nonroot
      convention.
- [ ] E2E / Chainsaw tests pass: the extension is registered (when
      `create_extension = true`), or the Cluster reaches Healthy with the image
      mounted for preload-only modules.
- [ ] `README.md` is clear and its `Cluster` example (and `Database` example
      when `create_extension = true`) are valid.
- [ ] `SECURITY-INSIGHTS.yml` has a matching `distribution-points` entry for
      the new image.
- [ ] PR targets `main` and is ready to merge.
