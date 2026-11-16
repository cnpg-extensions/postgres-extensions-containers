"""Exercise inventory boundaries and location-authoritative build dispatch."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow import discover, select


class DiscoveryTest(unittest.TestCase):
    def recipe(self, root, path, **fields):
        file = root / path / 'metadata.hcl'
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps({'name': Path(path).name,
                                    'versions': {'trixie': {'18': {'package': 'v1.0'}}},
                                    **fields}))

    def test_explicit_depth_and_location_override_legacy_metadata(self):
        with tempfile.TemporaryDirectory() as temp, patch('workflow.metadata', side_effect=lambda p: json.loads(p.read_text())):
            root = Path(temp)
            self.recipe(root, 'plain', build_system='pgrx')
            self.recipe(root, 'pgrx/rust', build_system='debian')
            self.recipe(root, 'universe/native', build_system='arbitrary')
            self.recipe(root, 'source-build/pgrx/templates/fixture')
            self.recipe(root, 'universe/native/test/fixture')
            inventory = discover(root)
            self.assertEqual(set(inventory), {'plain', 'rust', 'native'})
            self.assertEqual(inventory['plain']['build_family'], 'debian')
            self.assertEqual(inventory['rust']['recipe_path'], 'pgrx/rust')
            self.assertEqual(select({'extension_name': 'native', 'build_family': 'universe'}, inventory), ['linux/amd64', 'linux/arm64'])
            with self.assertRaisesRegex(ValueError, 'not in the pgrx'):
                select({'extension_name': 'native'}, inventory)

    def test_duplicate_names_fail_before_family_selection(self):
        with tempfile.TemporaryDirectory() as temp, patch('workflow.metadata', side_effect=lambda p: json.loads(p.read_text())):
            root = Path(temp)
            self.recipe(root, 'same')
            self.recipe(root, 'pgrx/same')
            with self.assertRaisesRegex(ValueError, 'duplicate logical'):
                discover(root)
