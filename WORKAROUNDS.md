# Upstream workarounds

Tracking the CloudNativePG upstream project is a high-priority goal. This register
covers intentional downstream workarounds and compatibility adaptations; choices
inherited from upstream do not require separate justification here.

On dependency updates, check the linked issue, pull request, or release contract,
verify the replacement, and remove temporary measures and their entries together
when they are no longer needed. Some entries describe packaging adaptations
rather than pending upstream bug fixes. Where no upstream issue is linked, say so
instead of implying that a fix is scheduled. Last reviewed: 2026-10-19.

Generator-specific dependency and license-reporting adaptations are maintained
in the [SBOM generator repository](https://github.com/cnpg-extensions/cnpg-sbom-generator/blob/main/WORKAROUNDS.md).

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
are documented in [BUILD.md](BUILD.md#usage-and-targets). PGRX uses the same selection policy through its own workflow.

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

## pglinter 2.0.0: missing Cargo.lock

- **Upstream:** [release 2.0.0](https://github.com/pmpetit/pglinter/tree/2.0.0)
  omits Cargo.lock. The first upstream lockfile was added in
  [d76a73d631b5435843917154a86e40c9d3889740](https://github.com/pmpetit/pglinter/commit/d76a73d631b5435843917154a86e40c9d3889740).
  No upstream issue is linked.
- **Problem:** our builder derives cargo-pgrx and dependency evidence from an
  upstream lockfile and requires locked dependency resolution.
- **Workaround:** [pglinter/Dockerfile](pglinter/Dockerfile) downloads that
  commit's Cargo.lock with a pinned SHA-256. It requires source version 2.0.0,
  the exact release Cargo.toml checksum, and an absent source lockfile before
  downloading. The borrowed lock still identifies pglinter 2.0.0 and pgrx 0.18.0;
  Cargo accepts it with the unmodified release manifest using `--locked`.
  Between the release and that commit, Cargo.toml only gains its license field
  and an exact pgrx-tests pin matching the locked version; Rust and SQL sources
  are unchanged. The existing cargo-about clarification mechanism supplies the
  missing Apache-2.0 declaration using the release LICENSE checksum.
- **Limits:** this is a later upstream dependency resolution, not a recovered
  lockfile from the original release build. Build evidence hashes the borrowed
  file as both original and effective lock inputs; the pinned download URL in
  the Dockerfile identifies its separate origin.
- **Review on every release:** the version guard deliberately stops the build
  even if Cargo.toml is otherwise unchanged. Prefer the next release's own
  lockfile; remove the download and guards after validating locked resolution,
  package inventory, licenses, native builds, and shared smoke checks. Revisit
  the license clarification if upstream ships `package.license`.

## pglinter: ARM64 fat LTO

- **Upstream:** [2.0.0 Cargo.toml](https://github.com/pmpetit/pglinter/blob/2.0.0/Cargo.toml)
  enables fat LTO and one codegen unit in the standard `release` profile.
  [Upstream CI](https://github.com/pmpetit/pglinter/blob/2.0.0/.github/actions/reusable-package-action-native/action.yml)
  selects `release-lto-off` on ARM64 to avoid runner memory exhaustion, as
  described in [PR #99](https://github.com/pmpetit/pglinter/pull/99).
- **Downstream decision:** [pglinter/Dockerfile](pglinter/Dockerfile) uses
  `--profile release` on both AMD64 and ARM64. We leave the upstream Cargo
  profiles unchanged and do not apply its CI setting that disables LTO.
- **Evidence:** on 2026-11-09, the [native ARM64 fat-LTO probe](https://github.com/ardentperf-labs/postgres-extensions-containers/actions/runs/42719148797)
  passed compilation, packaging, and Cargo/license evidence generation for
  PostgreSQL 18 on both Bookworm and Trixie using `ubuntu-24.04-arm` runners.
  BuildKit cgroup peak memory was 5,158,858,752 bytes on Bookworm and
  5,153,439,744 bytes on Trixie (about 4.8 GiB each), with zero OOM events on
  roughly 16 GB runners. The probe used pglinter 2.0.0, pgrx 0.18.0, Rust 1.97.1,
  and the borrowed lockfile documented above.
- **Limits:** the fat-LTO probe checked builds and evidence generation. The
  [full acceptance run](https://github.com/ardentperf-labs/postgres-extensions-containers/actions/runs/42718983690),
  including signing, security, provenance, and CNPG 1.30.1 smoke tests, passed
  with upstream's ARM64 LTO-disable setting.
- **Review when:** the extension, dependency lock, compiler, or runner resources
  change. Recheck native ARM64 builds and memory use before adopting any
  LTO-disable workaround.
