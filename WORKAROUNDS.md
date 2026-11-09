# Upstream workarounds

Tracking the CloudNativePG upstream project is a high-priority goal. This register
covers intentional downstream workarounds and compatibility adaptations; choices
inherited from upstream do not require separate justification here.

On dependency updates, check the linked issue, pull request, or release contract,
verify the replacement, and remove temporary measures and their entries together
when they are no longer needed. Some entries describe packaging adaptations
rather than pending upstream bug fixes. Where no upstream issue is linked, say so
instead of implying that a fix is scheduled. Last reviewed: 2026-10-19.

## Renovate: Debian security package lookups

- **Upstream:** [issue #44330](https://github.com/renovatebot/renovate/issues/44330)
  and [PR #35865](https://github.com/renovatebot/renovate/pull/35865), both open.
- **Problem:** the native `deb` datasource requests `Packages.gz`, but Bookworm
  security indexes are published as `Packages.xz`. Renovate skips the failed
  component and can report no updates even when a newer security package exists.
- **Workaround:** the two SBOM generator Debian rules in [renovate.json](renovate.json)
  use `custom.debian-bookworm` to read the full version from Debian's package
  details page for the requested architecture. The `plain` format lets JSONata
  inspect the HTML version heading, or the architecture's version table cell
  when Debian lists different binary rebuilds across architectures.
  This works with hosted Renovate and keeps Debian version ordering, existing
  grouping, and manual merge review.
  Package details include security updates and version epochs; download filenames
  omit epochs and must not be used as the version source. Architecture-independent
  packages also resolve through the architecture-specific details URLs.
- **Limits:** this depends on Debian's website layout and refresh cadence. A
  missing or changed version heading or ambiguous version cell fails the lookup
  instead of producing a guessed version. Package availability and dependency
  compatibility still need validation by the generator build.
- **Remove when:** the hosted Renovate release supports the security indexes.
  Restore the `deb` registry URLs for `bookworm`, `bookworm-updates`, and
  `bookworm-security` on each architecture, remove the datasource overrides and
  custom datasource, and verify a security-only update is proposed on both
  architectures with the correct epochs.

## Syft: readability of hash-based license references

- **Upstream:** [issue #3527: Unable to classify complex licenses](https://github.com/anchore/syft/issues/3527).
  This [comment](https://github.com/anchore/syft/issues/3527#issuecomment-6295475239)
  discusses the usability of hash-based results.
  [PR #5448](https://github.com/anchore/syft/pull/5448), currently open, proposes
  more descriptive custom references for possible license matches below the
  configured coverage threshold.
- **Problem:** complex Debian copyright notices can appear in license reports
  as hash-based custom references. The license evidence is retained, but a hash
  alone gives users little help understanding it.
- **Current approach:** the SBOM generator passes through Syft's license
  references and extracted text while scoping package and file records to the
  shipped payload. Original notices are shipped in `/licenses`. Users can start with a checksum in Grant and retrieve the
  original notice. See [reading license results](sbom-generator/README.md#reading-license-results).
- **Limits:** a hash identifies text; it does not explain its terms. PR #5448
  proposes `LicenseRef-Possible-<ID>-<hash>` names containing candidate license
  IDs and a shortened source-text hash. These remain custom references, not
  assertions of standard SPDX licenses. Complex notices may still need manual
  review, and scanner accuracy remains an upstream Syft concern.
- **Revisit when:** a released Syft version includes the upstream usability
  improvement. Upgrade the pin and check how candidate references and their
  extracted text appear in SPDX and Grant, then update the checksum-based
  reading guidance as appropriate.

## unit: mounted data-file paths

- **Upstream:** [postgresql-unit](https://github.com/df7cb/postgresql-unit) and its
  PGDG package. No upstream issue or pull request is currently linked. This is a
  CNPG packaging adaptation rather than a confirmed upstream defect.
- **Problem:** packaged installation and upgrade SQL hard-codes Debian's
  `/usr/share/postgresql/18/extension` data-file paths, while CNPG mounts this
  extension image below `/extensions/unit`.
- **Workaround:** [unit/Dockerfile](unit/Dockerfile) applies
  [the SQL path patch](unit/patches/0001-use-cnpg-mounted-data-files.patch) to all
  14 data-file reads, pointing them at `/extensions/unit/share/extension`. The
  patched SQL and original data files are shipped together. See
  [unit/README.md](unit/README.md) for maintenance context.
- **Review when:** the package's SQL scripts, data-file loading, or CNPG mount
  layout changes. Retain the patch until the packaged SQL can load the mounted
  files without it; verify extension creation and affected upgrade paths before
  removing it.

## CI: SLSA provenance retries

- **Upstream:** [SLSA generator v2.1.0](https://github.com/slsa-framework/slsa-github-generator/blob/v2.1.0/.github/workflows/generator_container_slsa3.yml).
  No upstream issue or pull request is currently linked.
- **Problem:** generator errors produce a successful job with a failure output;
  only the separate `final` job fails. Retrying failed jobs reuses that output.
- **Workaround:** [the retry workflow](.github/workflows/retry-failed-builds.yml)
  reruns the matching `detect-env` job and its dependents, including the generator,
  for an isolated provenance failure. Multiple or mixed failures, or an unmatched
  job, retry the full workflow once; ordinary failures retain the failed-jobs retry.
- **Remove when:** the pinned SLSA workflow fails generator jobs directly and
  GitHub's failed-jobs retry reruns their work.

## CI: extension rebuild selection

Before extension-scoped build selection, shared CI changes triggered the full
extension matrix, then repeated on merge to `main`. Successful runs show the scale:
the 2026-10-14 Bake action update completed
[834 branch jobs](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/runs/38609995588)
and [919 more after merge](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/runs/38621555543).
On 2026-10-17, the shared [kubectl digest update](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/runs/39006667971)
and [psql digest update](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/runs/39006736993)
completed 1,915 jobs each. These counts exclude skipped jobs.
Shared changes now select a representative sample on non-main branches and do not
trigger production rebuilds on `main`. Direct extension payload changes still
build automatically. The sample and manual single/all-extension rebuild commands
are documented in [BUILD.md](BUILD.md#usage-and-targets). PGRX is outside this
selection policy.

## PostgreSQL Anonymizer 3.3.2: stale root Cargo.lock version

- **Upstream:** [3.3.2 Cargo.lock](https://gitlab.com/dalibo/postgresql_anonymizer/-/blob/3.3.2/Cargo.lock)
  records `anon` as 3.3.1 while Cargo.toml declares 3.3.2. No upstream issue is linked.
- **Problem:** locked Cargo fetch rejects the inconsistent release before compilation.
- **Workaround:** [postgresql-anonymizer/Dockerfile](postgresql-anonymizer/Dockerfile)
  changes only the root package version to 3.3.2, guarded by exact original and
  effective lock checksums. Both hashes remain in build evidence; dependencies
  are unchanged.
- **Remove when:** the next source release has a consistent root version.
  Review or remove the correction whenever the upstream lock changes, then run
  the native image build and shared smoke checks.
