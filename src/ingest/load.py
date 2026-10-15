"""
load.py - read the trials back off disk into memory.
=====================================================
Standard library only (csv).

A "trial" dict looks like:
    {
      "trial_id": 3,
      "config_id": "5_120_Right_0",
      "label": 0 or 1,            # is_off_nominal
      "meta": {...},              # speed, radius, etc.
      "data": { "current1": [..floats..], "vel1_rad_s": [...], ... },
      "n": number_of_samples,
    }
"""

import os
import csv


def load_trials(processed_dir="data/processed"):
    """Load every trial listed in _trials_index.csv."""
    index_path = os.path.join(processed_dir, "_trials_index.csv")
    trials = []

    for meta in csv.DictReader(open(index_path)):
        csv_path = os.path.join(processed_dir, meta["csv_path"])

        # read the time series into {column: [values]}
        data = {}
        reader = csv.DictReader(open(csv_path))
        for col in reader.fieldnames:
            data[col] = []
        for row in reader:
            for col in reader.fieldnames:
                data[col].append(float(row[col]))

        trials.append({
            "trial_id": int(meta["trial_id"]),
            "config_id": meta["config_id"],
            "label": int(meta["is_off_nominal"]),
            "meta": meta,
            "data": data,
            "n": int(meta["n_samples"]),
        })

    return trials


if __name__ == "__main__":
    ts = load_trials()
    print("loaded %d trials" % len(ts))
    print("first trial id=%s config=%s label=%s samples=%s"
          % (ts[0]["trial_id"], ts[0]["config_id"], ts[0]["label"], ts[0]["n"]))
