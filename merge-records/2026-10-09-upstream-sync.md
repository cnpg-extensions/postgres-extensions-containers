# Upstream Sync Commit Review

Reviewed locally on 2026-10-09.

- Mirror ref: `origin/main` at `50e209e18358255051808e5168c5b4158bdb5a58` (`cnpg-extensions/postgres-extensions-containers`)
- Working branch: `upstream/sync-2026-10-09`, to be published to a validation fork
- Upstream ref: `upstream/main` at `019e7c20e8feb930a61e4799c108462c3b63485b` (`cloudnative-pg/postgres-extensions-containers`)
- Last upstream commit already merged: `c1c47c21fb6ffa7ff46d19f019e8d6502dc8ffec`
- Downstream merge commit: `28f0cb2e579baa6c43c8498dff46438c274c1c20` (second parent is the upstream SHA above).
- Reviewed commits: 30; substantive: 8; pure dependency chores: 22.

## Review rules

Exact changed paths are checked against the mirror SHA above. Dependency-only
commits are consolidated by area using final cumulative values, rather than
replayed individually. Preserve all downstream extension directories and
metadata, including paths Git pairs with upstream PostGIS through rename detection.

## Consolidated dependency-only updates

| Area | Reviewed commits (full SHA, date, subject) | Final value and decision |
| --- | --- | --- |
| kubectl | `7c799ff376c16400469117716364273e11971bf9` (2026-09-15, chore(deps): update alpine/kubectl:1.37.0 docker digest to 601225d (#336))<br>`e40655c7c6f60df92750e00c4179c8c04a239641` (2026-09-21, chore(deps): update alpine/kubectl:1.37.0 docker digest to 954b65d (#350))<br>`cd6b832982d4b95c1cee97d3813fe4c8a5ae960f` (2026-09-28, chore(deps): update alpine/kubectl docker tag to v1.37.1 (#357))<br>`6a3015b832ba2e4748fef26796b7019810048c10` (2026-10-05, chore(deps): update alpine/kubectl:1.37.1 docker digest to b57b3bd (#364)) | Retain already-current downstream final `1.37.1@sha256:b57b3bd3cd9f4f02dd444281857126aa78efa4b7b7e6ec57579dd927bf146fc3` in `Taskfile.yml`. |
| GitHub actions | `cc6c6d4a835b3d73ac53e8c7f4af4e6702f4fd25` (2026-09-17, chore(deps): update all github action (#340)) | Final QEMU `99012661954931238ded8c8b007157a8430204e1`, Buildx `f87e5991a6d7451dcb8d9637bfbc97413f497069` and Bake `018cb6412ab401ebaa809aa5f85966b74628600f` are already downstream; retain them and adopt checkout pin in the new cleanup workflow. |
| psql | `9ee367e658eafb5f87606f5402b0ba36e00cb358` (2026-09-17, chore(deps): update alpine/psql:18.6 docker digest to 2042ec7 (#337))<br>`97ba392d763ea4f520ad08a79ea03edfd88b3f29` (2026-09-21, chore(deps): update alpine/psql:18.6 docker digest to 60d0642 (#351))<br>`efdac5c0f3eb249c3a7347dc9922fc0b53eced1d` (2026-09-28, chore(deps): update alpine/psql:18.6 docker digest to 794901a (#356))<br>`6374a18ffb58a6d309766b4df575da8e32e385b5` (2026-10-05, chore(deps): update alpine/psql:18.6 docker digest to a783fb5 (#365)) | Retain already-current downstream final `18.6@sha256:a783fb5128d77638813e17e9ae5e400acfdd627a9d2073e1eea05b20c81a5a4b` in shared `test/check-extension.yaml`; exclude upstream-only extension tests. |
| Alpine toolbox | `28042fa367c7d850dac35a402472b0bcc007feac` (2026-09-21, chore(deps): update alpine:3.24 docker digest to 294b683 (#347)) | Retain already-current downstream final `3.24@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6` in `Taskfile.yml`. |
| Local registry | `61fdef699c312f78c52c141eab3e1f1791cfb229` (2026-09-21, chore(deps): update registry:3.1.1 docker digest to fd374ba (#348))<br>`dcd023a73ff6a07a5fea82b72df43da871dc1b70` (2026-09-22, chore(deps): update registry:3.1.1 docker digest to 325b4b2 (#352))<br>`263b9d64c5c336716f3c65b11cf40daab2e3004d` (2026-09-25, chore(deps): update registry docker tag to v3.1.2 (#355))<br>`d3d118aadb0ed0d9ec8a9f266b83028eb46e5181` (2026-09-29, chore(deps): update registry:3.1.2 docker digest to ddf7543 (#359)) | Retain already-current downstream final `3.1.2@sha256:ddf754342cfc8acc51a56d5d0ab6af06826461864460636d8bd5c546dab2a7b8` in `Taskfile.yml`. |
| CI runners | `cc2e308252cce47ade9690b673e96e20b5ed296e` (2026-09-22, chore(deps): update dependency ubuntu to v26 (#349)) | Adopt `ubuntu-26.04` for updated shared jobs; retain existing conditional build runner selection. |
| Upstream-only extension packages | `ed70a120135b563a424cee25e61495962a27f156` (2026-09-22, chore(deps): update dependency postgresql-18-pg-ivm (#343))<br>`2b63d8ecc33b595abfddee76b863a68a057f8d34` (2026-09-22, chore(deps): update dependency postgresql-18-timescaledb (#344))<br>`df52088af39e9716464e2c59c9e1228f5de0a791` (2026-09-25, chore(deps): update dependency postgresql-18-pgvector (#354))<br>`cbfe3ef27782831f9760071fd4e1d65d78bb0232` (2026-09-25, chore(deps): update dependency postgresql-18-pg-crash (#353))<br>`6f9c4e4f657a61f7c3c7d1404e9bd1facf131139` (2026-10-07, chore(deps): update dependency postgresql-18-pgvector (#366))<br>`3fae74d74e2b553abd0a55b7da4397d5c3782292` (2026-10-07, chore(deps): update dependency postgresql-18-timescaledb (#361)) | Exclude all pg-ivm, timescaledb-oss, pgvector and pg-crash package/README changes. |
| Dagger | `5cf97fe4eebf6baddbd75b89a9171c09fccb0c8d` (2026-10-01, chore(deps): update dependency dagger/dagger to v0.21.10 (#360)) | Retain downstream `0.21.10` CLI/workflow/engine pins and adopt it for the new cleanup workflow. Keep module declaration `v0.21.7` unchanged, as upstream does. |

## Planned adoption

| Date | Upstream commit | Subject | Touches mirror files? | Relevant paths | Decision |
| --- | --- | --- | :---: | --- | --- |
| 2026-09-14 | `40def1c4cc3c2d80fe71da3aacccee0b116c5b3a` | ci: add workflow to cleanup -testing operand image (#314) | No | absent: `.github/workflows/registry-clean.yml` | Adopt the metadata-driven testing-image retention workflow, scoped to the downstream repository owner. |
| 2026-09-16 | `b9cad7649aa1d7e23cca993225e36e7bc0d7777f` | fix(maintenance): handle Debian epoch versions (#333) | Yes | mirror: `dagger/maintenance/image.go`<br>mirror: `dagger/maintenance/image_test.go`<br>mirror: `renovate.json` | Adapt the remaining single-component version support and tests; retain downstream malformed-epoch rejection, image registry and Renovate policy already ported. |
| 2026-10-07 | `81714c1d933e0b078fabbbc861b72c41cb418f79` | test: use CNPG released versions instead of testing release branches (#367) | Yes | mirror: `.github/workflows/bake_targets.yml`<br>mirror: `Taskfile.yml` | Adopt released patch-version smoke tests and release-manifest selection; preserve downstream catalog installation. |

## Not relevant

| Date | Upstream commit | Subject | Touches mirror files? | Relevant paths | Decision |
| --- | --- | --- | :---: | --- | --- |
| 2026-09-14 | `6c8483b985ad5b4005e529bf04f04a6e3af72b44` | chore: sync generated files with cnpg-infra policy (#341) | No | absent: `.github/ISSUE_TEMPLATE/component-owner-proposal.yml`<br>absent: `.gitvote.yml`<br>absent: `COMPONENT_OWNERS.md` | Exclude upstream governance, voter teams and component-owner nomination policy; retain downstream ownership. |
| 2026-09-15 | `b20d2213118b49cd220160fff8edad7724928204` | fix: require a strict majority to pass a gitvote vote (#342) | No | absent: `.gitvote.yml` | Exclude upstream-only GitVote policy; downstream has no GitVote configuration. |
| 2026-09-22 | `337c3873fe973b098d42ebe32315da34794991e2` | chore: update postgis OS libraries (#331) | No | absent: `postgis/system-libs/18-bookworm-os-libs.txt`<br>absent: `postgis/system-libs/18-trixie-os-libs.txt` | Exclude upstream-only PostGIS library manifests, including rename-based conflicts with downstream extension paths. |
| 2026-10-07 | `a002df12e834795f94807b5deab7e76f9f42b116` | chore: sync generated files with cnpg-infra policy (#368) | No | absent: `COMPONENT_OWNERS.md` | Exclude upstream component-owner and reviewer assignments. |
| 2026-10-07 | `019e7c20e8feb930a61e4799c108462c3b63485b` | chore: update postgis OS libraries (#358) | No | absent: `postgis/system-libs/18-bookworm-os-libs.txt`<br>absent: `postgis/system-libs/18-trixie-os-libs.txt` | Exclude upstream-only PostGIS library manifests; preserve downstream system-library lists. |

## Conflict decisions

- `dagger/maintenance/image.go` and `image_test.go`: adapt upstream single-component
  version support while retaining the downstream registry and malformed-epoch
  regression test. Add a trailing boundary so `1:pkg-1` cannot fall back to
  matching `1`; accept both `1:8-1.pgdg12+1` and `8-1.pgdg12+1`.
- `renovate.json`: retain downstream. Epoch conversion was already ported;
  upstream's additional nested replacement of `.` with `.` does not change
  the intended template behavior. Preserve downstream stable-release and SQL
  version review rules and `cnpg-extensions` README image matching.
- Restore all extension paths to the downstream base, including automatically
  merged changes. Rename detection paired upstream paths with
  `mobilitydb/system-libs/18-bookworm-os-libs.txt`,
  `mobilitydb/system-libs/18-trixie-os-libs.txt`, `pg-stat-plans/metadata.hcl`,
  and `timestamp9/metadata.hcl`; all are preserved exactly.
- Remove resurrected upstream-only pg-crash, pg-ivm, pgrouting, pgvector,
  postgis, timescaledb-oss, and wal2json paths.
- Exclude new upstream `.gitvote.yml`, `COMPONENT_OWNERS.md`, and the
  component-owner nomination issue template. Downstream `CODEOWNERS`, README,
  security metadata, branding and ownership remain unchanged.
- Adopt the new registry cleanup workflow with upstream's dynamic
  `github.repository_owner` account and downstream metadata-derived image
  names. It deletes only matching testing images older than one week,
  retaining at least the most recent version per image.
- Adopt released CNPG patch versions for smoke tests and manifest selection;
  retain downstream catalog installation in `e2e:install-cnpg`.
- Retain already-current downstream shared image/action/Dagger pins.
  Adopt upstream Ubuntu 26.04 labels in the shared jobs changed upstream.


## Validation

- `git diff --cached --check` passed; no unresolved index entries remain.
- `task --summary` parsed the merged Taskfile.
- Generated the ignored Dagger client with installed CLI v0.21.9; restored
  the unchanged module declaration after generation. With the same dummy
  session variables as CI, `go test ./...` passed in `dagger/maintenance`.
- `task checks:all` passed for all 84 downstream extension targets with no
  warnings. Full log: local `/tmp/upstream-sync-20261009-checks.log`.
- actionlint v1.7.12 passed for all six affected workflows with ShellCheck
  disabled and a temporary config accepting `ubuntu-26.04`. Its bundled
  runner list is outdated; GitHub's current official
  [runner image list](https://github.com/actions/runner-images#available-images)
  confirms that hosted label is available. No repository lint suppression
  was added.
- Executed the smoke-matrix shell against live CNPG tags: result
  `["main","1.29.3","1.30.1"]`. All three selected manifest URLs returned
  Deployment manifests; incomplete `1.30` and prerelease `1.30.1-rc1`
  inputs were rejected by the Taskfile manifest selector.
- Executed the registry-clean image-list shell against all downstream
  metadata: 84 unique nonempty names, all ending in `-testing`.
  No registry cleanup action was executed during validation.
- Reviewed the staged delta: only shared workflows, Taskfile, maintenance
  version parsing/tests, and this new record. All extension files,
  `CODEOWNERS`, README, security metadata and Renovate policy are unchanged.
  Newly added `cloudnative-pg` references only identify upstream CNPG tags
  and manifests; downstream image/catalog identity is preserved.
- Full image builds, cluster E2E smoke tests, and GitHub-hosted CI have not
  been run locally; they remain for PR CI.
