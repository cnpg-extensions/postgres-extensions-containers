// Execute inside the pinned Renovate image. Only /tmp is writable.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { extractPackageFile } from '/usr/local/renovate/dist/modules/manager/custom/regex/index.js';
import { doAutoReplace } from '/usr/local/renovate/dist/workers/repository/update/branch/auto-replace.js';
import { applyPackageRules } from '/usr/local/renovate/dist/util/package-rules/index.js';
import { GlobalConfig } from '/usr/local/renovate/dist/config/global.js';

GlobalConfig.set({ localDir: '/tmp/renovate-update-fixture' });
const config = JSON.parse(await fs.readFile('/repo/renovate.json', 'utf8'));
const rootEntries = await fs.readdir('/repo', { withFileTypes: true });
const sourceCases = [];
for (const entry of rootEntries.filter(item => item.isDirectory())) {
  const packageFile = entry.name + '/metadata.hcl';
  let content;
  try {
    content = await fs.readFile('/repo/' + packageFile, 'utf8');
  } catch {
    continue;
  }
  if (!/\bbuild_system\s*=\s*"pgrx"/.test(content)) continue;

  const manager = config.customManagers.find(value => value.description.startsWith('PGRX source tags'));
  assert(manager, 'PGRX source manager');
  const extracted = extractPackageFile(content, packageFile, manager);
  assert(extracted?.deps.length, packageFile);
  const repository = content.match(/source_repository\s*=\s*"https:\/\/(?:github|gitlab)\.com\/([^"]+)"/);
  assert(repository, 'canonical source_repository in ' + packageFile);
  const expectedDepName = repository[1].replace(/\.git$/, '');
  const expectedVersions = [...new Set([...content.matchAll(/\bpackage\s*=\s*"([^"]+)"/g)]
    .map(match => match[1]))].sort();
  const actualVersions = [...new Set(extracted.deps.map(dependency => {
    assert.equal(dependency.depName, expectedDepName, packageFile);
    return dependency.currentValue;
  }))].sort();
  assert.deepEqual(actualVersions, expectedVersions, packageFile);
  sourceCases.push([packageFile, 'PGRX source tags']);
}
assert(sourceCases.length > 0, 'PGRX metadata files discovered');

const cases = [
  ...sourceCases,
  ['pgrx/dependencies/tools.json', 'PGRX workflow/build tool releases'],
  ['pgrx/dependencies/workflow-tools.json', 'PGRX workflow/build tool releases'],
  ['pgrx/dependencies/workflow-tools.json', 'PGRX digest-pinned execution images'],
  ['.github/workflows/pgrx_targets.yml', 'updates the Taskfile'],
  ['.github/workflows/pgrx-tests.yml', 'updates the Taskfile'],
  ['.github/workflows/cnpg-versions.yml', 'updates the Taskfile'],
];
let count = 0;
for (const [packageFile, prefix] of cases) {
  const manager = config.customManagers.find(value => value.description.startsWith(prefix));
  assert(manager, prefix);
  const content = await fs.readFile('/repo/' + packageFile, 'utf8');
  const extracted = extractPackageFile(content, packageFile, manager);
  assert(extracted?.deps.length, packageFile);
  for (const [depIndex, dependency] of extracted.deps.entries()) {
    if (prefix === 'updates the Taskfile' && !['ghcr.io/cnpg-extensions/cnpg-sbom-generator', 'cloudnative-pg/cloudnative-pg'].includes(dependency.depName)) continue;
    let change = dependency.currentDigest
      ? { newDigest: (dependency.currentDigest.startsWith('sha256:') ? 'sha256:' : '') + 'a'.repeat(dependency.currentDigest.replace('sha256:', '').length) }
      : { newValue: dependency.currentValue.startsWith('v') ? 'v999.0.0' : '999.0.0' };
    const updated = await doAutoReplace({ ...manager, ...extracted, ...dependency, ...change,
      manager: 'regex', packageFile, depIndex }, content, false);
    assert.notEqual(updated, content, dependency.depName);
    const reextracted = extractPackageFile(updated, packageFile, manager).deps[depIndex];
    assert.equal(reextracted.currentValue, change.newValue ?? dependency.currentValue);
    assert.equal(reextracted.currentDigest, change.newDigest ?? dependency.currentDigest);
    if (dependency.depName === 'quay.io/skopeo/stable') {
      assert.match(dependency.currentValue, /^v\d+\.\d+\.\d+-immutable$/);
      const newValue = 'v999.0.0-immutable';
      const newDigest = 'sha256:' + 'b'.repeat(64);
      const immutableUpdated = await doAutoReplace({ ...manager, ...extracted, ...dependency,
        newValue, newDigest, manager: 'regex', packageFile, depIndex }, content, false);
      const immutableReextracted = extractPackageFile(immutableUpdated, packageFile, manager).deps[depIndex];
      assert.equal(immutableReextracted.currentValue, newValue);
      assert.equal(immutableReextracted.currentDigest, newDigest);
      assert.match(immutableUpdated, /quay\.io\/skopeo\/stable:v999\.0\.0-immutable@sha256:b{64}/);
      count++;
    }
    if (packageFile.endsWith('/metadata.hcl')) {
      assert.deepEqual(updated.match(/sql\s*=\s*"[^"]+"/g), content.match(/sql\s*=\s*"[^"]+"/g));
    }
    count++;
  }
}

// Exercise resolved policy, including a future source repository name. PGRX
// overrides must not change shared GitHub Action grouping or image digest pins.
for (const [packageFile, depName, datasource, groupName, pinDigests, automerge] of [
  ['pg-durable/metadata.hcl', 'microsoft/pg_durable', 'github-tags', null, false, false],
  ['pg-durable/metadata.hcl', 'future-owner/future-source', 'github-tags', null, false, false],
  ['postgresql-anonymizer/metadata.hcl', 'dalibo/postgresql_anonymizer', 'gitlab-tags', null, false, false],
  ['pgrx/dependencies/tools.json', 'rust-lang/rust', 'github-releases', undefined, true, false],
  ['.github/workflows/pgrx.yml', 'actions/checkout', 'github-tags', 'all github action', true, true],
]) {
  const resolved = await applyPackageRules({ packageFile, depName, datasource,
    manager: 'regex', updateType: 'patch', pinDigests: true, automerge: true,
    packageRules: config.packageRules }, 'pre-lookup');
  assert.equal(resolved.groupName, groupName, packageFile);
  assert.equal(resolved.pinDigests, pinDigests, packageFile);
  assert.equal(resolved.automerge, automerge, packageFile);
}
console.log(JSON.stringify({ success: true, replacementsChecked: count }));
