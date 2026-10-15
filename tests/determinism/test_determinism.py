"""
test_determinism.py - same seed MUST give the same result, twice.
This is the baby version of spec rule #3 (bit-exact / reproducible).
Run:  python3 tests/determinism/test_determinism.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from ingest import synth
from ingest.load import load_trials
from preprocessing.splits import group_split


def run_once(seed):
    tmp = tempfile.mkdtemp()
    synth.generate_dataset(out_dir=tmp, n_configs=4, trials_per_config=4, seed=seed)
    trials = load_trials(tmp)
    splits = group_split(trials, {"train": 0.6, "val": 0.2, "test": 0.2},
                         seed=seed, group_key="trial_id")
    # capture: the first trial's first current reading + the test trial ids
    signature = (
        round(trials[0]["data"]["current1"][0], 6),
        tuple(sorted(t["trial_id"] for t in splits["test"])),
    )
    return signature


def main():
    a = run_once(42)
    b = run_once(42)
    assert a == b, "same seed gave different results:\n  %r\n  %r" % (a, b)

    c = run_once(43)
    assert a != c, "different seeds gave identical results (seed ignored?)"
    print("PASS test_determinism: seed 42 repeats exactly; seed 43 differs")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("FAIL test_determinism:", e)
        sys.exit(1)
