import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from assemble import check_assembly
from record import validate_record


def native_index(architecture, number):
    child = 'sha256:' + str(number) * 64
    return {'manifests': [
        {'mediaType': 'application/vnd.oci.image.manifest.v1+json',
         'digest': child, 'size': 1234,
         'platform': {'os': 'linux', 'architecture': architecture}},
        {'mediaType': 'application/vnd.oci.image.manifest.v1+json',
         'digest': 'sha256:' + str(number + 1) * 64, 'size': 5678,
         'platform': {'os': 'unknown', 'architecture': 'unknown'},
         'annotations': {'vnd.docker.reference.type': 'attestation-manifest',
                         'vnd.docker.reference.digest': child}},
    ]}


class AssemblyTest(unittest.TestCase):
    platforms = ['linux/amd64', 'linux/arm64']

    def setUp(self):
        self.sources = [native_index('amd64', 1), native_index('arm64', 3)]

    def merged(self):
        return {'manifests': copy.deepcopy([
            descriptor for source in self.sources for descriptor in source['manifests']
        ])}

    def test_complete_native_indexes_can_be_merged_in_any_order(self):
        merged = self.merged()
        merged['manifests'].reverse()
        check_assembly(merged, self.sources, self.platforms)

    def test_merge_must_preserve_every_source_descriptor(self):
        for change in ['drop', 'digest', 'size', 'platform', 'attachment']:
            with self.subTest(change=change):
                merged = self.merged()
                if change == 'drop':
                    merged['manifests'].pop()
                elif change == 'attachment':
                    merged['manifests'][1]['annotations']['vnd.docker.reference.digest'] = 'sha256:' + '9' * 64
                else:
                    merged['manifests'][0][change] = {
                        'digest': 'sha256:' + '9' * 64,
                        'size': 9999,
                        'platform': {'os': 'linux', 'architecture': 'arm64'},
                    }[change]
                with self.assertRaisesRegex(ValueError, 'changed descriptors'):
                    check_assembly(merged, self.sources, self.platforms)

    def test_preserving_sources_is_insufficient_when_a_platform_is_missing(self):
        self.sources.pop()
        with self.assertRaisesRegex(ValueError, 'missing expected platform'):
            check_assembly(self.merged(), self.sources, self.platforms)

    def test_two_native_builds_for_the_same_platform_do_not_complete_the_matrix(self):
        self.sources[1] = native_index('amd64', 3)
        with self.assertRaisesRegex(ValueError, 'duplicate platform'):
            check_assembly(self.merged(), self.sources, self.platforms)

    def test_source_indexes_must_include_one_attestation_per_native_image(self):
        for mistake in ['missing', 'duplicate', 'wrong-subject']:
            with self.subTest(mistake=mistake):
                self.setUp()
                descriptors = self.sources[1]['manifests']
                if mistake == 'missing':
                    descriptors.pop()
                elif mistake == 'duplicate':
                    descriptors.append(copy.deepcopy(descriptors[1]))
                else:
                    descriptors[1]['annotations']['vnd.docker.reference.digest'] = self.sources[0]['manifests'][0]['digest']
                with self.assertRaisesRegex(ValueError, 'platform attestation'):
                    check_assembly(self.merged(), self.sources, self.platforms)


class AssemblyRecordTest(unittest.TestCase):
    def test_downloaded_record_belongs_to_the_expected_row_and_preparation(self):
        row = {'id': 'pg18-trixie-amd64', 'target': 'pg18-trixie',
               'platform': 'linux/amd64', 'staging': 'registry.test/extension:native-amd64'}
        preparation = {'git_sha': 'commit', 'timestamp': '2026-11-09T00:00:00Z',
                       'preparation_sha256': 'prepared-inputs', 'run_id': '123-2',
                       'workspace_sha256': 'workspace', 'generator': {'version': '1'}}
        index_digest = 'sha256:' + 'a' * 64
        record = {**preparation, 'schema_version': 1, 'row': row,
                  'image': 'registry.test/extension@' + index_digest,
                  'index_digest': index_digest}
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory)
            (artifact / 'record.json').write_text(json.dumps(record))
            self.assertEqual(validate_record(preparation, row, artifact), record)
            replacements = {
                'row': {**row, 'id': 'pg18-trixie-arm64', 'platform': 'linux/arm64'},
                'preparation_sha256': 'previous-preparation',
                'run_id': '123-1',
                'workspace_sha256': 'previous-workspace',
                'image': 'registry.test/another-extension@' + index_digest,
            }
            for field, replacement in replacements.items():
                with self.subTest(field=field):
                    (artifact / 'record.json').write_text(json.dumps({**record, field: replacement}))
                    with self.assertRaises(ValueError):
                        validate_record(preparation, row, artifact)


if __name__ == '__main__':
    unittest.main()
