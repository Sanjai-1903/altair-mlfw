"""
test_splits_no_leakage.py - prove a trial never lands in two sets, and
that windows from one trial stay on one side. This is spec rule #2.
Run:  python3 tests/unit/test_splits_no_leakage.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from ingest import synth
from ingest.load import load_trials
from preprocessing.splits import group_split, assert_no_leakage
from preprocessing.windows import make_windows


def main():
    tmp = tempfile.mkdtemp()
    synth.generate_dataset(out_dir=tmp, n_configs=6, trials_per_config=5, seed=2)
    trials = load_trials(tmp)

    splits = group_split(trials, {"train": 0.6, "val": 0.2, "test": 0.2},
                         seed=2, group_key="trial_id")

    # 1. the explicit gate check must pass
    assert_no_leakage(splits, group_key="trial_id")

    # 2. independently: no trial_id appears in two sets
    ids = {name: set(t["trial_id"] for t in splits[name])
           for name in ("train", "val", "test")}
    assert not (ids["train"] & ids["test"]), "train/test share a trial!"
    assert not (ids["train"] & ids["val"]), "train/val share a trial!"
    assert not (ids["val"] & ids["test"]), "val/test share a trial!"

    # 3. every window's trial_id belongs to the set it came from
    for name in ("train", "val", "test"):
        wins = make_windows(splits[name], synth.FEATURES, 50, 25)
        for w in wins:
            assert w["trial_id"] in ids[name], "a window leaked out of %s" % name

    total = len(ids["train"]) + len(ids["val"]) + len(ids["test"])
    assert total == len(trials), "lost or duplicated trials in the split"
    print("PASS test_splits_no_leakage: 30 trials, disjoint sets, windows stay put")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("FAIL test_splits_no_leakage:", e)
        sys.exit(1)
