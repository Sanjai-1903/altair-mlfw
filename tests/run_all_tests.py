"""
run_all_tests.py - run every test and report a tally.
Run:  python3 tests/run_all_tests.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = [
    "data_contract/test_schema.py",
    "unit/test_splits_no_leakage.py",
    "determinism/test_determinism.py",
]

fails = 0
for rel in TESTS:
    path = os.path.join(HERE, rel)
    print("--- running", rel)
    r = subprocess.run([sys.executable, path])
    if r.returncode != 0:
        fails += 1

print("\n%d/%d test files passed" % (len(TESTS) - fails, len(TESTS)))
sys.exit(1 if fails else 0)
