"""
run_pipeline.py - the whole P1->P2 pipeline, start to finish.
=============================================================
Standard library only. Run it from the repo root:

    python3 run_pipeline.py            # uses existing data (or makes it)
    python3 run_pipeline.py --regen    # throw away data and regenerate

What it does, in order:
  1. read the config files
  2. make synthetic data if none exists
  3. load trials
  4. SPLIT BY TRIAL  (then check: no leakage)   <- spec rule #2
  5. cut windows, turn each into a feature vector
  6. fit baselines B0..B3 on train, tune on val
  7. open the TEST set exactly ONCE and score everyone
  8. write a report and a row in experiments/index.csv

Nothing here trains an SNN. The baselines set the bar the SNN must beat.
"""

import os
import sys
import csv
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from util import miniyaml                     # noqa: E402
from ingest import synth                      # noqa: E402
from ingest.load import load_trials           # noqa: E402
from preprocessing.splits import group_split, assert_no_leakage  # noqa: E402
from preprocessing.windows import (           # noqa: E402
    make_windows, window_features, feature_names)
from baseline.baselines import all_baselines  # noqa: E402
from baseline.metrics import evaluate         # noqa: E402

WINDOW_SIZE = 50        # samples (1.0 s at 50 Hz)
STRIDE = 25             # samples (0.5 s step -> 50% overlap)


def build_matrix(windows, feat_cols):
    """Turn a list of windows into X (feature vectors) and y (labels)."""
    X = [window_features(w, feat_cols) for w in windows]
    y = [w["label"] for w in windows]
    return X, y


def main():
    regen = "--regen" in sys.argv

    dataset_cfg = miniyaml.load(os.path.join(HERE, "configs", "dataset.yaml"))
    splits_cfg = miniyaml.load(os.path.join(HERE, "configs", "splits.yaml"))

    feat_cols = dataset_cfg["feature_columns"]
    processed_dir = os.path.join(HERE, dataset_cfg["processed_dir"])
    rate = dataset_cfg["sample_rate_hz"]
    window_seconds = WINDOW_SIZE / float(rate)

    print("=" * 64)
    print(dataset_cfg["banner"])
    print("source:", dataset_cfg["source"])
    print("=" * 64)

    # 1-2. make data if needed
    index_file = os.path.join(processed_dir, "_trials_index.csv")
    if regen or not os.path.exists(index_file):
        if dataset_cfg["source"] != "synthetic":
            raise SystemExit("source is not synthetic but no data found: "
                             "point processed_dir at the real data.")
        print("generating synthetic data ...")
        synth.generate_dataset(out_dir=processed_dir, seed=splits_cfg["seed"])

    # 3. load
    trials = load_trials(processed_dir)
    n_off = sum(t["label"] for t in trials)
    print("loaded %d trials (%d off-nominal, %d nominal)"
          % (len(trials), n_off, len(trials) - n_off))

    # 4. split by whole trial, then PROVE there is no leakage
    splits = group_split(trials, splits_cfg["ratios"],
                         seed=splits_cfg["seed"],
                         group_key=splits_cfg["split_by"])
    assert_no_leakage(splits, group_key=splits_cfg["split_by"])
    print("split -> train %d / val %d / test %d trials  (no leakage OK)"
          % (len(splits["train"]), len(splits["val"]), len(splits["test"])))

    # 5. windows + features (made AFTER the split)
    names = feature_names(feat_cols)
    Xtr, ytr = build_matrix(make_windows(splits["train"], feat_cols, WINDOW_SIZE, STRIDE), feat_cols)
    Xval, yval = build_matrix(make_windows(splits["val"], feat_cols, WINDOW_SIZE, STRIDE), feat_cols)
    Xte, yte = build_matrix(make_windows(splits["test"], feat_cols, WINDOW_SIZE, STRIDE), feat_cols)
    print("windows -> train %d / val %d / test %d" % (len(Xtr), len(Xval), len(Xte)))

    # 6-7. fit each baseline, then open TEST once
    print("\nopening the TEST set once, scoring baselines:\n")
    header = "%-20s %7s %7s %7s %9s %12s" % (
        "baseline", "prec", "recall", "f1", "falseAl%", "falseAl/hr")
    print(header)
    print("-" * len(header))

    results = []
    for model in all_baselines():
        model.fit(Xtr, ytr, Xval, yval, names)
        preds = model.predict(Xte)
        m = evaluate(yte, preds, window_seconds)
        m["name"] = model.name
        results.append(m)
        print("%-20s %7.3f %7.3f %7.3f %9.2f %12.1f" % (
            model.name, m["precision"], m["recall"], m["f1"],
            100 * m["false_alarm_rate"], m["false_alarms_per_hour"]))

    # the bar the SNN must beat
    best = max(results, key=lambda r: r["f1"])
    print("\nbest baseline: %s  (F1 = %.3f)" % (best["name"], best["f1"]))
    print("--> the SNN must clearly beat this AND fit GF180, or it is NO-GO.")

    # 8. write report + index row
    write_outputs(results, best, splits, dataset_cfg, window_seconds)


def write_outputs(results, best, splits, dataset_cfg, window_seconds):
    reports_dir = os.path.join(HERE, "experiments", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = "run_" + stamp

    report = os.path.join(reports_dir, run_id + ".md")
    with open(report, "w") as f:
        f.write("# Baseline report %s\n\n" % run_id)
        f.write("**%s**\n\n" % dataset_cfg["banner"])
        f.write("- data source: `%s`\n" % dataset_cfg["source"])
        f.write("- trials: train %d / val %d / test %d\n" % (
            len(splits["train"]), len(splits["val"]), len(splits["test"])))
        f.write("- window: %.2fs | test set opened once\n\n" % window_seconds)
        f.write("| baseline | precision | recall | f1 | false-alarm %% | false-alarm/hr |\n")
        f.write("|---|---|---|---|---|---|\n")
        for m in results:
            f.write("| %s | %.3f | %.3f | %.3f | %.2f | %.1f |\n" % (
                m["name"], m["precision"], m["recall"], m["f1"],
                100 * m["false_alarm_rate"], m["false_alarms_per_hour"]))
        f.write("\n**Best baseline: %s (F1 = %.3f).** "
                "The SNN must clearly beat this AND fit the GF180, "
                "or the honest recommendation is NO-GO.\n" % (best["name"], best["f1"]))

    index = os.path.join(HERE, "experiments", "index.csv")
    new = not os.path.exists(index)
    with open(index, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["run_id", "timestamp", "data_source",
                        "n_train_trials", "n_val_trials", "n_test_trials",
                        "best_baseline", "best_f1", "report"])
        w.writerow([run_id, stamp, dataset_cfg["source"],
                    len(splits["train"]), len(splits["val"]), len(splits["test"]),
                    best["name"], "%.3f" % best["f1"],
                    os.path.relpath(report, HERE)])
    print("\nwrote %s" % os.path.relpath(report, HERE))
    print("appended experiments/index.csv")


if __name__ == "__main__":
    main()
