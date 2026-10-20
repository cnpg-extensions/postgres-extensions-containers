import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from workflow import select,changed_extensions

class SelectorTest(unittest.TestCase):
    inventory={'pg-session-jwt':{'versions':{'trixie':{'18':{}},'bookworm':{'18':{}}}},'pg-durable':{'versions':{'trixie':{'18':{}}}}}
    def test_hosted_selects_both_native_architectures(self):
        self.assertEqual(select({'extension_name':'pg-session-jwt'},self.inventory),['linux/amd64','linux/arm64'])
        self.assertEqual(select({'extension_name':'pg-durable','cnpg_version':'1.30'},self.inventory),['linux/amd64','linux/arm64'])
        with self.assertRaises(ValueError):select({'extension_name':'pg-unknown'},self.inventory)
    def test_paths(self):
        self.assertEqual(changed_extensions(['sbom-generator/generator.py'],self.inventory),[])
        self.assertEqual(changed_extensions(['pg-durable/Dockerfile'],self.inventory),['pg-durable'])
        self.assertEqual(changed_extensions(['pgrx/sbom/augment_spdx.py'],self.inventory),sorted(self.inventory))
