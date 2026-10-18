# Upstream workarounds

Tracking the CloudNativePG upstream project is a high-priority goal. This register
covers intentional downstream workarounds and compatibility adaptations; choices
inherited from upstream do not require separate justification here.

On dependency updates, check the linked issue, pull request, or release contract,
verify the replacement, and remove temporary measures and their entries together
when they are no longer needed. Some entries describe packaging adaptations
rather than pending upstream bug fixes. Where no upstream issue is linked, say so
instead of implying that a fix is scheduled. Last reviewed: 2026-10-18.

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

## ScanCode: Pluggy compatibility pin

- **Upstream:** [ScanCode issue #5363](https://github.com/aboutcode-org/scancode-toolkit/issues/5363),
  open.
- **Problem:** Pluggy `1.7.0` breaks ScanCode `32.5.0` plugin registration with
  `ValueError: did not find any 'pre_scan' hooks`.
- **Workaround:** `pluggy==1.6.0` in
  [sbom-generator/requirements.txt](sbom-generator/requirements.txt). Renovate's
  SBOM dependency group includes a reminder to retry without this compatibility
  hold whenever ScanCode is updated. Retain normal dependency locking after
  removing the special hold; installation uses `--no-deps` and `pip check`.
- **Remove when:** a released ScanCode/Pluggy combination fixes registration.
  Update the resolved Pluggy version and remove the special pin comments and
  Renovate reminder after the native AMD64 and ARM64 generator integration
  checks pass with the newer combination.

## ScanCode: system native libraries on ARM64

- **Upstream:** ScanCode's native dependencies, notably
  [ExtractCode](https://github.com/aboutcode-org/extractcode) and
  [TypeCode](https://github.com/aboutcode-org/typecode). No upstream issue or
  pull request is currently linked for this adaptation.
- **Problem:** the bundled native libraries are not available on every
  architecture. Native ARM64 validation also exposed failed libarchive discovery.
- **Workaround:** [sbom-generator/Dockerfile](sbom-generator/Dockerfile) installs
  Debian's `libarchive13` and `libmagic1` (with its magic database), creates the
  libarchive alias, and sets `EXTRACTCODE_LIBARCHIVE_PATH` and
  `TYPECODE_LIBMAGIC_DB_PATH`. The Python requirements retain architecture-specific
  versions of the bundled native-library packages where their available releases
  differ.
- **Remove when:** released dependencies provide working libraries and discovery
  on both AMD64 and ARM64. Verify ScanCode startup and the existing native
  generator integration checks before removing the system-library dependencies,
  alias, environment overrides, or architecture-specific requirements.

## ScanCode: large Debian copyright files

- **Upstream:** [ScanCode Toolkit](https://github.com/aboutcode-org/scancode-toolkit).
  No upstream issue or pull request is currently linked for this workaround.
- **Problem:** Debian copyright files can contain thousands of `License:`
  sections; scanning a combined file can exceed ScanCode's per-file timeout.
- **Workaround:** `prepare_license_scan_root` in
  [sbom-generator/generator.py](sbom-generator/generator.py) uses `csplit` to scan
  smaller sections, then maps ScanCode results back to the original notice paths.
  Original shipped notices remain intact.
- **Remove when:** representative large notices scan completely within the
  supported ScanCode limits without splitting. Compare license evidence and
  original file attribution before removing the chunk preparation and path
  normalization, and rerun the generator integration checks on both architectures.

## ScanCode: Python version compatibility

- **Upstream:** the supported Python versions for
  [ScanCode Toolkit 32.5.0](https://github.com/aboutcode-org/scancode-toolkit/releases/tag/v32.5.0).
  This is a release compatibility constraint, not a separately tracked bug.
- **Workaround:** [sbom-generator/Dockerfile](sbom-generator/Dockerfile) stays on
  Python `3.14-slim-bookworm`, the newest Python supported by the selected ScanCode
  release, rather than accepting a newer Python solely because Renovate offers it.
- **Remove when:** the selected ScanCode release supports a newer Python.
  Update the base-image pin and compatibility comments together and verify Python
  dependency installation, ScanCode startup, and native AMD64/ARM64 integration.

## ScanCode: SPDX Tools compatibility pin

- **Upstream:** [ScanCode Toolkit 32.5.0's dependency declaration](https://github.com/aboutcode-org/scancode-toolkit/blob/v32.5.0/requirements.txt)
  requires `spdx-tools==0.8.2`. This is a release compatibility constraint, not a
  separately tracked bug.
- **Workaround:** [sbom-generator/requirements.txt](sbom-generator/requirements.txt)
  retains `spdx-tools==0.8.2`. Renovate groups validator changes with ScanCode
  dependencies for compatibility review instead of accepting an independent bump.
- **Remove when:** the selected ScanCode release permits a newer SPDX Tools
  version. Update the resolved requirements together and run `pip check` and the
  native generator integration checks, including final SPDX validation.

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
