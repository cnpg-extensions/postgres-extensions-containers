#!/usr/bin/env python3
"""Run the downstream suite, including composition with the core generator."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
suite=unittest.TestLoader().discover(str(ROOT/'pgrx/tests'),pattern='test_*.py')
if not suite.countTestCases():raise RuntimeError('empty test discovery: pgrx/tests')
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
