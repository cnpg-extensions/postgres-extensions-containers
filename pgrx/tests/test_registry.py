import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from registry import wait_for_index_digest


class RegistryTagTest(unittest.TestCase):
    reference = 'registry.test/extension:version'
    index = {'schemaVersion': 2, 'mediaType': 'application/vnd.oci.image.index.v1+json',
             'manifests': [], 'annotations': {'org.opencontainers.image.revision': 'new'}}
    current = json.dumps(index).encode()
    digest = 'sha256:' + hashlib.sha256(current).hexdigest()

    @patch('registry.time.sleep')
    @patch('registry.subprocess.check_output')
    def test_stale_tag_is_rechecked_until_exact_index_is_visible(self, inspect, sleep):
        previous = json.dumps({**self.index, 'annotations': {'org.opencontainers.image.revision': 'old'}}).encode()
        inspect.side_effect = [previous, self.current]
        wait_for_index_digest(self.reference, self.digest)
        self.assertEqual(2, inspect.call_count)
        sleep.assert_called_once_with(2)

    @patch('registry.time.sleep')
    @patch('registry.subprocess.check_output')
    def test_new_tag_can_be_temporarily_unavailable(self, inspect, sleep):
        inspect.side_effect = [subprocess.CalledProcessError(1, ['docker']), self.current]
        wait_for_index_digest(self.reference, self.digest)
        self.assertEqual(2, inspect.call_count)

    @patch('registry.time.sleep')
    @patch('registry.subprocess.check_output')
    def test_retries_do_not_accept_changed_index_bytes(self, inspect, sleep):
        # Even semantically equal JSON has a different content-addressed identity.
        inspect.return_value = json.dumps(self.index, indent=2).encode()
        with self.assertRaisesRegex(ValueError, 'expected sha256:.*got sha256:'):
            wait_for_index_digest(self.reference, self.digest, attempts=3)
        self.assertEqual(3, inspect.call_count)
        self.assertEqual(2, sleep.call_count)
