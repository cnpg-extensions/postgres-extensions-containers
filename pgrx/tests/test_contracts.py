import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare import digest
from record import load_preparation


class PreparationTest(unittest.TestCase):
    def test_stale_or_tampered_preparation(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary);value={'workspace_sha256':'current'};value['preparation_sha256']=digest(value)
            (path/'preparation.json').write_text(json.dumps(value))
            with patch('record.source_digest',return_value='current'):self.assertEqual(load_preparation(path),value)
            with patch('record.source_digest',return_value='changed'),self.assertRaisesRegex(ValueError,'workspace'):load_preparation(path)
            value['workspace_sha256']='changed';(path/'preparation.json').write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'checksum'):load_preparation(path)
