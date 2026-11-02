# Upstream Merge Instructions

This file gives agents a repeatable process for synchronizing the CNPG
Extensions repository with its upstream template while preserving the
downstream extension set and the complete upstream history.

## Repositories

- Downstream: `https://github.com/cnpg-extensions/postgres-extensions-containers`
- Upstream: `https://github.com/cloudnative-pg/postgres-extensions-containers`

The downstream repository is the source of truth for the extensions it
publishes. Upstream changes to individual extension directories and extension
versions are intentionally not mirrored unless a maintainer explicitly asks
for them. Shared build infrastructure, maintenance code, workflows, security
metadata, and generally applicable documentation should be reviewed for each
upstream sync.

## Merge records

The append-only [merge-records/](./merge-records/) directory is the source of
truth for upstream syncs. The newest ISO-date-named record is the latest sync.
Each record contains the exact upstream and downstream commit SHAs. Future
merges must not require an edit to this file.

## Merge record directory

Store one detailed review record per upstream sync under `merge-records/`.
Use an immutable date-based filename such as
`merge-records/2026-09-02-upstream-sync.md`; never overwrite an earlier
record.

Each record must include the exact mirror ref, upstream ref, last upstream
commit already merged, every substantive upstream commit reviewed, the
consolidated dependency note, planned adoptions, intentional exclusions,
conflict decisions, downstream behavioral-impact decisions, and validation
results.

The directory also contains an inherited historical baseline marker. Future
records should begin from the upstream commit recorded by the newest record.

Keep the records append-only in normal use. If a historical correction is
needed, preserve the original text and add a dated correction note.

## Procedure for a future sync

1. Start from an up-to-date downstream `main` or a working branch based on
   it. Keep the worktree clean, fetch both remotes, and record the exact
   upstream tip before resolving anything:

   ```sh
   git fetch origin main
   git fetch upstream main
   git status --short
   git rev-parse upstream/main
   git show -s --format='%H%n%aI%n%s' upstream/main
   ```

2. Compare the upstream tip with the commit recorded in the newest dated
   record under `merge-records/`. Review upstream commits and use a non-mutating
   merge preview when practical:

   ```sh
   git merge-base downstream/main upstream/main
   git log --oneline --left-right downstream/main...upstream/main
   git merge-tree --write-tree downstream/main upstream/main
   ```

   Create a new dated record under `merge-records/` before changing code;
   use normal Git inspection commands and the first record as the format
   reference. For each commit in the range, inspect its summary and changed
   paths, then check whether each path exists at the mirror ref:

   ```sh
   git show --stat --summary <full-upstream-sha>
   git diff-tree --no-commit-id --name-status -r <full-upstream-sha>
   git cat-file -e "origin/main:<changed-path>" 2>/dev/null
   ```

   Keep pure `chore(deps):` commits out of the two detailed tables and
   summarize them once by dependency area, using final cumulative versions
   relevant to the mirror. The detailed record must have separate
   **Planned adoption** and **Not relevant** tables. Every non-dependency row
   must include the full 40-character SHA, date, subject, whether any exact
   changed path exists in the mirror, relevant paths, and a short adoption or
   exclusion comment.

   For each substantive shared-infrastructure change, review whether its
   intent should also affect the downstream PGRX path, even if Git merges
   cleanly or the changed file has no PGRX counterpart. Trace relevant callers
   and parallel implementations, including target discovery and cleanup,
   build and release gates, security and provenance, catalog publication,
   smoke-test support policy, and tool updates. Record the affected downstream
   paths, the decision to adopt, adapt, retain the difference, or defer, the
   reason, and relevant validation. Different behavior is acceptable when
   intentional; a clean merge alone does not complete this review.

3. Create a real merge commit with `upstream/main` as its second parent. Do
   not rebase the downstream work onto upstream and do not replace the merge
   with a collection of cherry-picks. Preserving ancestry makes the exact
   upstream sync point auditable and keeps later merges manageable.

   When the upstream-sync branch is submitted as a pull request, merge it
   with GitHub's **Create a merge commit** option. Do not squash or rebase an
   upstream-sync pull request, because either strategy can flatten the
   upstream ancestry needed for future syncs. Squashing remains acceptable
   for unrelated documentation-only pull requests that do not incorporate
   upstream history.

4. Resolve conflicts by intent:

   - Keep downstream versions of extension directories and their metadata;
     do not pull in upstream extension additions or version bumps.
   - Review and normally port upstream changes to shared workflows, Dagger
     maintenance code, `docker-bake.hcl`, `Taskfile.yml`, tests, and general
     documentation.
   - Manually merge `README.md` and security metadata. `CODEOWNERS` is
     downstream-owned: CNPG Extensions has its own ownership model, so never
     copy upstream `CODEOWNERS` changes or component-owner assignments. Keep
     downstream branding, custom image locations, and policy links.
   - Check repository and image identity values for accidental
     `cloudnative-pg` references before finalizing the merge.

5. Before creating the merge commit, create a new dated detailed record in
   `merge-records/` using the exact SHA captured in step 1. After the merge
   commit is created, add its exact downstream SHA to the new record. Do not
   edit `MERGE.md`; the newest dated record becomes the latest sync
   automatically. The recorded upstream SHA must be the commit actually
   merged, not merely the newest commit observed during review.

6. Run the relevant validation. At minimum, review the merge diff for
   extension-directory changes and run the repository checks affected by the
   sync. For maintenance-code changes, run the Dagger Go tests; for workflow
   or build changes, run the applicable Task/build checks and CI validation.

7. In the pull request description, include:

   - the full upstream SHA merged;
   - the downstream base and merge commit once available;
   - the intentional extension-directory exclusions;
   - conflicts requiring manual adaptation; and
   - validation performed.
