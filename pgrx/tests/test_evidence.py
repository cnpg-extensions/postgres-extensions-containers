import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import normalize_about
from sbom.augment_spdx import license_expression


class ReporterCompatibilityTest(unittest.TestCase):
    def test_identical_doctest_boolean_is_canonicalized(self):
        raw = b'{"targets":[{"doctest":true,"doctest":true}]}'
        normalized = normalize_about(raw)
        self.assertEqual(json.loads(normalized), {'targets': [{'doctest': True}]})
        self.assertEqual(normalize_about(normalized), normalized)

    def test_conflicting_or_identity_duplicates_fail(self):
        for raw in [b'{"doctest":true,"doctest":false}',
                    b'{"doctest":1,"doctest":1}',
                    b'{"id":"same","id":"same"}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                normalize_about(raw)

    def test_hyphenated_spdx_identifiers_survive_generation(self):
        for expression in ['BSD-3-Clause-No-Nuclear-Warranty',
                           'GPL-2.0-only WITH GCC-exception-2.0',
                           'LGPL-3.0-or-later', 'CC-BY-NC-ND-3.0-IGO']:
            self.assertEqual(license_expression(expression), expression)
