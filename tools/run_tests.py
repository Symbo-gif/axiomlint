"""Unittest discovery with explicit anti-empty / anti-all-skipped checks."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))


def run() -> int:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    count = suite.countTestCases()
    if count == 0:
        print("FAIL: zero discovered tests", file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.testsRun == 0 or len(result.skipped) == result.testsRun:
        print("FAIL: zero executed non-skipped tests", file=sys.stderr)
        return 1
    print(f"COUNTS discovered={count} executed={result.testsRun} skipped={len(result.skipped)}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(run())

