"""
windows.py - cut each trial into fixed-size windows and summarise them.
=======================================================================
Standard library only (math).

A model does not look at a whole 12-second trial at once. It looks at
short WINDOWS (say 1 second = 50 samples) as they stream in. We slide a
window along the trial with a step ("stride").

IMPORTANT: windows are made AFTER the split (see splits.py). A window
keeps the label and trial_id of the trial it came from.

For the simple baselines we turn each window into a short list of
numbers (mean, std, min, max, rms per signal). That list is the
"feature vector".
"""

import math


def make_windows(trials, feature_columns, window_size=50, stride=25):
    """Return a flat list of window dicts from all the given trials."""
    windows = []
    for t in trials:
        n = t["n"]
        start = 0
        while start + window_size <= n:
            piece = {}
            for col in feature_columns:
                piece[col] = t["data"][col][start:start + window_size]
            windows.append({
                "trial_id": t["trial_id"],
                "config_id": t["config_id"],
                "label": t["label"],
                "signals": piece,
            })
            start += stride
    return windows


def _mean(xs):
    return sum(xs) / len(xs)


def _std(xs, mean):
    # population standard deviation, kept simple
    total = 0.0
    for x in xs:
        total += (x - mean) * (x - mean)
    return math.sqrt(total / len(xs))


def _rms(xs):
    total = 0.0
    for x in xs:
        total += x * x
    return math.sqrt(total / len(xs))


def feature_names(feature_columns):
    """The names of the numbers window_features() produces, in order."""
    names = []
    for col in feature_columns:
        for stat in ("mean", "std", "min", "max", "rms"):
            names.append(col + "_" + stat)
    return names


def window_features(window, feature_columns):
    """Turn one window into a flat list of numbers (the feature vector)."""
    vector = []
    for col in feature_columns:
        xs = window["signals"][col]
        m = _mean(xs)
        vector.append(m)
        vector.append(_std(xs, m))
        vector.append(min(xs))
        vector.append(max(xs))
        vector.append(_rms(xs))
    return vector
