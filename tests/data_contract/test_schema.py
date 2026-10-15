"""
test_schema.py - the data must match the contract (Gate G2 helper).
Run:  python3 tests/data_contract/test_schema.py
Exits 0 if PASS, 1 if FAIL. No pytest needed.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from ingest import synth
from ingest.load import load_trials

REQUIRED = ["time_s"] + synth.FEATURES


def main():
    tmp = tempfile.mkdtemp()
    synth.generate_dataset(out_dir=tmp, n_configs=3, trials_per_config=3, seed=1)
    trials = load_trials(tmp)

    assert len(trials) == 9, "expected 9 trials, got %d" % len(trials)
    for t in trials:
        for col in REQUIRED:
            assert col in t["data"], "missing column %s" % col
        assert t["label"] in (0, 1), "label must be 0/1"
        assert t["n"] == len(t["data"]["time_s"]), "n_samples mismatch"
    print("PASS test_schema: 9 trials, all required columns present, labels 0/1")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("FAIL test_schema:", e)
        sys.exit(1)
