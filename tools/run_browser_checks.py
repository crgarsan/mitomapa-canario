#!/usr/bin/env python3
"""Run unittest suites and expose failures as readable GitHub annotations."""

import argparse
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def annotation(value):
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("patterns", nargs="+", help="unittest file patterns within tests/")
    args = parser.parse_args()
    suite = unittest.TestSuite()
    for pattern in args.patterns:
        selected = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern=pattern)
        if selected.countTestCases() == 0:
            parser.error(f"No tests found for {pattern}")
        suite.addTests(selected)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    for test, traceback in result.errors + result.failures:
        print("::error title=Prueba de navegador::" + annotation(f"{test}\n{traceback}"), flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
