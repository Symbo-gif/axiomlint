"""Run a declared package's trusted tests; reject empty/all-skipped selections."""

import argparse
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))


def run(package: str, root: Path = ROOT) -> int:
    if not re.fullmatch(r"WP-(00[1-9]|0[12][0-9]|03[0-6])", package):
        raise ValueError("Package must be WP-001 through WP-036")
    pattern = f"test_wp_{package[-3:]}_*.py"
    suite = unittest.TestLoader().discover(str(root / "tests"), pattern=pattern)
    count = suite.countTestCases()
    if count == 0:
        print(f"BLOCKED: {package} has no targeted executable tests ({pattern})", file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.testsRun == 0 or result.testsRun == len(result.skipped):
        print(f"BLOCKED: {package} executed no non-skipped tests", file=sys.stderr)
        return 1
    print(f"PACKAGE={package} discovered={count} executed={result.testsRun} skipped={len(result.skipped)}")
    return 0 if result.wasSuccessful() else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package")
    args = parser.parse_args()
    try:
        return run(args.package)
    except ValueError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
