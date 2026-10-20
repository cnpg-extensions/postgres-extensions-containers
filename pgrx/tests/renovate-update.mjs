// Execute inside the pinned Renovate image. Only /tmp is writable.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { extractPackageFile } from '/usr/local/renovate/dist/modules/manager/custom/regex/index.js';
import { doAutoReplace } from '/usr/local/renovate/dist/workers/repository/update/branch/auto-replace.js';
import { applyPackageRules } from '/usr/local/renovate/dist/util/package-rules/index.js';
import { filterVersions } from '/usr/local/renovate/dist/workers/repository/process/lookup/filter.js';
import { get as getVersioning } from '/usr/local/renovate/dist/modules/versioning/index.js';
import { GlobalConfig } from '/usr/local/renovate/dist/config/global.js';

GlobalConfig.set({ localDir: '/tmp/renovate-update-fixture' });
const config = JSON.parse(await fs.readFile('/repo/renovate.json', 'utf8'));
const sourcePins = JSON.parse(await fs.readFile('/repo/pgrx/dependencies/sources.json', 'utf8'));
const cases = [
  ...Object.keys(sourcePins).map(name => [name + '/metadata.hcl', 'PGRX source tags']),
  ...['tools', 'workflow-tools'].map(name => ['pgrx/dependencies/' + name + '.json', 'PGRX workflow/build tool']),
  ['pgrx/dependencies/workflow-tools.json', 'PGRX digest-pinned'],
  ['pgrx/dependencies/bases.json', 'PGRX base indexes'],
  ['pgrx/dependencies/fixtures/lock.json', 'PGRX CNPG operator release tags'],
  ['pgrx/dependencies/fixtures/lock.json', 'PGRX CNPG catalog fixture commits'],
  ['.github/workflows/pgrx_targets.yml', 'updates the Taskfile'],
];
const cnpgReleaseRules = config.packageRules.filter(value => value.description?.startsWith('Keep CNPG '));
assert.equal(cnpgReleaseRules.length, 2, 'CNPG release tag line rules');
let count = 0;
for (const [packageFile, prefix] of cases) {
  const manager = config.customManagers.find(value => value.description.startsWith(prefix));
  assert(manager, prefix);
  const content = await fs.readFile('/repo/' + packageFile, 'utf8');
  const extracted = extractPackageFile(content, packageFile, manager);
  assert(extracted?.deps.length, packageFile);
  for (const [depIndex, dependency] of extracted.deps.entries()) {
    if (prefix === 'updates the Taskfile' && dependency.depName !== 'ghcr.io/cnpg-extensions/cnpg-sbom-generator') continue;
    let change = dependency.currentDigest
      ? { newDigest: (dependency.currentDigest.startsWith('sha256:') ? 'sha256:' : '') + 'a'.repeat(dependency.currentDigest.replace('sha256:', '').length) }
      : { newValue: dependency.currentValue.startsWith('v') ? 'v999.0.0' : '999.0.0' };
    if (prefix === 'PGRX CNPG operator release tags') {
      const version = dependency.currentValue.match(/^v(\d+)\.(\d+)\.(\d+)$/);
      assert(version, dependency.currentValue);
      assert.equal(dependency.datasource, 'github-tags');
      assert.equal(dependency.versioning, 'semver');
      assert.equal(dependency.packageName, 'cloudnative-pg/cloudnative-pg');
      assert.equal(dependency.depName, 'https://github.com/cloudnative-pg/cloudnative-pg');
      const lineRule = cnpgReleaseRules.find(rule => new RegExp(rule.matchCurrentValue.slice(1, -1)).test(dependency.currentValue));
      assert(lineRule, `missing minor line rule for ${dependency.currentValue}`);
      assert.equal(lineRule.allowedVersions, lineRule.matchCurrentValue);
      const ruleConfig = await applyPackageRules({ ...dependency, packageRules: config.packageRules,
        manager: 'regex', packageFile, updateType: 'patch' }, 'pre-lookup');
      assert.equal(ruleConfig.allowedVersions, lineRule.allowedVersions);
      change = { newValue: `v${version[1]}.${version[2]}.${Number(version[3]) + 1}`, newDigest: 'b'.repeat(40) };
      const nextMinorTag = `v${version[1]}.${Number(version[2]) + 1}.0`;
      const eligible = filterVersions({ ...ruleConfig, ignoreUnstable: true }, dependency.currentValue, undefined,
      [{ version: change.newValue }, { version: nextMinorTag }], getVersioning(dependency.versioning));
      assert.deepEqual(eligible.map(release => release.version), [change.newValue]);
    }
    if (prefix === 'PGRX CNPG catalog fixture commits') {
      assert.equal(dependency.datasource, 'git-refs');
      assert.equal(dependency.currentValue, 'main');
    }
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
    // A version proposal must leave checksum refresh to its explicit owner.
    if (change.newValue && packageFile.endsWith('.json')) {
      assert.deepEqual(updated.match(/"sha256":\s*"[a-f0-9]+"/g), content.match(/"sha256":\s*"[a-f0-9]+"/g));
    }
    count++;
  }
}
console.log(JSON.stringify({ success: true, replacementsChecked: count }));
