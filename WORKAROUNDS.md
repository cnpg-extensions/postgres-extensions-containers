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

## Grant: terminal table formatting

- **Upstream:** [PR #556](https://github.com/anchore/grant/pull/556), merged as
  [`63b3f99949ef9f4a9962b7a9bc74d44f7ecd483d`](https://github.com/anchore/grant/commit/63b3f99949ef9f4a9962b7a9bc74d44f7ecd483d).
  The latest release, `v0.6.8`, does not include it.
- **Problem:** wide license columns make terminal reports difficult to read.
- **Workaround:** [examples/sbom-reports.txt](examples/sbom-reports.txt) records
  how to build the unreleased fixed commit used for the captured report. This
  applies to the reporting example; CI continues to use the released Grant image
  and its JSON output.
- **Remove when:** a Grant release includes the fix. Update the example's build
  instructions and recapture its reports with that release, checking long
  license expressions and terminal wrapping. Keep the capture provenance accurate.

## Syft: Debian license coverage

- **Upstream:** [issue #3527: Unable to classify complex licenses](https://github.com/anchore/syft/issues/3527),
  open, describes missing license results for Debian copyright files containing
  multiple licenses and other text. [Issue #4133](https://github.com/anchore/syft/issues/4133),
  also open, concerns a less specific `GPL` result for `base-files` where the
  notice specifies GPL version 2 or later. These are relevant references; the
  exact issue consulted when ScanCode was originally adopted was not recorded.
- **Problem:** Syft's Debian license results can be missing or incomplete.
  This is not simply an inability to read package metadata: the
  [pinned Syft 1.54.1 implementation](https://github.com/anchore/syft/blob/v1.54.1/syft/pkg/cataloger/debian/package.go)
  reads package copyright files, parses license declarations, and falls back to
  classifying the file's text when parsing produces no license values. That
  fallback does not supplement a nonempty but incomplete set of declarations.
  Notices can also place incorporated-code license references in comments or
  exceptions in the license body rather than in the `License:` label. Whole-file
  classification of complex notices can miss evidence even when it is present.
- **Workaround:** keep Syft for package inventory and ownership, and use ScanCode
  to scan all shipped `/licenses` notices independently of Syft's license results.
  [The generator](sbom-generator/README.md#reading-license-results) records the
  evidence on SPDX files and their owning packages, and fills missing or unknown
  package declarations. This complements existing declarations rather than
  replacing every declaration with the scanner's interpretation.
- **Limits:** `NOASSERTION` results in a recent maintainer spot-check of a CNPG
  PostgreSQL image motivate reassessment, but do not establish the cause of each
  missing result or a measured advantage for ScanCode. Neither scanner proves
  which terms govern a shipped binary: shared notices can cover an entire source
  package, and classification can produce false positives. Preserve the notices
  and evidence for review.
- **Revisit when:** compare the current Syft release with the ScanCode path on
  the same representative images and notices, including complex Debian files,
  additional license references, and exceptions. Check missing results, incorrect
  matches, and package/file attribution before removing ScanCode. The section
  splitting described below is a candidate for discussion on Syft #3527; no
  upstream proposal or evidence that it fixes Syft's classifier is recorded yet.

## ScanCode: ARM64 release archive and Debian packaging

- **Upstream:** [issue #3958: Support arm64/aarch64](https://github.com/aboutcode-org/scancode-toolkit/issues/3958),
  open. [Fedora packages are available](https://github.com/aboutcode-org/scancode-toolkit/issues/3958#issuecomment-2599746956),
  but the selected stable ScanCode 32.5.0 release has no Linux ARM64 application
  archive or Debian package suitable for our Debian-based images.
- **Workaround:** install ScanCode through pip using the selected release's
  upstream dependency pins. Pip is currently the available installation path
  for both architectures in our Debian-based generator image. ScanCode minor and
  patch updates automerge after the required checks pass; major updates require
  manual merging.
- **Remove when:** a stable Linux ARM64 release archive or suitable Debian package
  is available. Adopt it after both native generator integration checks pass.
  This is an installation packaging gap; Python remains part of the generator.

## ScanCode: Linux ARM64 support

- **Upstream:** [issue #3958: Support arm64/aarch64](https://github.com/aboutcode-org/scancode-toolkit/issues/3958),
  open. [Issue #3304](https://github.com/aboutcode-org/scancode-toolkit/issues/3304),
  also open, reports the same ExtractCode/7z constraint conflict on Apple ARM.
  [Issue #2271](https://github.com/aboutcode-org/scancode-toolkit/issues/2271),
  open, tracks finding system binaries when bundled native providers are absent.
- **Problem:** ScanCode 32.5.0's upstream native dependency pins have no Linux
  ARM64 wheels. An ARM64 build using the unchanged upstream requirements fails
  during pip resolution at `extractcode-7z==16.5.210531`. System libarchive
  discovery also needed an explicit path in our native ARM64 validation.
- **Workaround:** [sbom-generator/Dockerfile](sbom-generator/Dockerfile) removes
  the `extractcode-7z`, `extractcode-libarchive`, and `typecode-libmagic` pins from
  the downloaded constraints on ARM64. Pip selects compatible versions using
  ScanCode's dependency ranges and available ARM64 distributions. It also
  installs Debian's `libarchive13` and `libmagic1` with its magic database,
  creates the libarchive alias, and sets `EXTRACTCODE_LIBARCHIVE_PATH` and
  `TYPECODE_LIBMAGIC_DB_PATH`.
- **Remove when:** a stable ScanCode release supplies working Linux ARM64
  installation and native library discovery. Retry the unchanged upstream
  constraints, then remove the constraint exclusions and system-library
  adaptations once ScanCode startup and both native generator integration checks
  pass.

## ScanCode: large Debian copyright files

- **Upstream:** [ScanCode Toolkit](https://github.com/aboutcode-org/scancode-toolkit).
  No upstream issue or pull request is currently linked for this workaround.
- **Problem:** Debian copyright files can contain thousands of `License:`
  sections; scanning a combined file can exceed ScanCode's per-file timeout.
  Splitting was introduced for resource and timeout limits; maintainer validation
  also found that it substantially improved license recognition on these notices.
- **Workaround:** `prepare_license_scan_root` in
  [sbom-generator/generator.py](sbom-generator/generator.py) uses `csplit` to scan
  smaller sections, then maps ScanCode results back to the original notice paths.
  Original shipped notices remain intact.
  This addresses a similar multi-license input problem to
  [Syft #3527](https://github.com/anchore/syft/issues/3527), but uses a different
  classifier and has not been validated as a fix for Syft.
- **Remove when:** representative large notices scan completely within the
  supported ScanCode limits without splitting. Compare license evidence and
  original file attribution before removing the chunk preparation and path
  normalization, and rerun the generator integration checks on both architectures.

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

## CI: extension rebuilds (option not adopted)

Shared CI changes trigger the full extension matrix, then repeat on merge to
`main`. Successful runs show the scale: the 2026-10-14 Bake action update completed
[834 branch jobs](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/runs/38609995588)
and [919 more after merge](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/runs/38621555543).
On 2026-10-17, the shared [kubectl digest update](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/runs/39006667971)
and [psql digest update](https://github.com/cnpg-extensions/postgres-extensions-containers/actions/runs/39006736993)
completed 1,915 jobs each. These counts exclude skipped jobs.
The [ci/extension-build-selection branch](https://github.com/ardentperf-labs/postgres-extensions-containers/tree/ci/extension-build-selection)
proposes a representative sample on branches and no infrastructure-only rebuilds
on `main`; directly changed extensions still build. The proposed Debian sample is
`pgtap`, `pg-cron`, `ogr-fdw`, and `powa`; the separate
[PGRX branch](https://github.com/ardentperf-labs/postgres-extensions-containers/tree/ci/pgrx-build-selection)
uses `pg-session-jwt` and `pg-durable`. This option is not adopted.
