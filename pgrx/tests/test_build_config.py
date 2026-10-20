from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_config import effective_features,RECIPES

class BuildConfigTest(unittest.TestCase):
    def test_pg_search_preserves_non_pg_defaults(self):
        self.assertEqual(effective_features({'features':{'default':['pg18','deferred_wal']}},RECIPES['pg-search'],18),['deferred_wal','pg18'])
    def test_jwt_replaces_pg17_default(self):
        self.assertEqual(effective_features({'features':{'default':['pg17']}},RECIPES['pg-session-jwt'],18),['pg18'])
    def test_explicit_no_default_features(self):
        for name in ['pg-durable','pg-jsonschema','pg-parquet']:
            self.assertEqual(effective_features({'features':{'default':['pg17','optional']}},RECIPES[name],18),['pg18'])
