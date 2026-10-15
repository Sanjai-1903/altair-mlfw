"""
splits.py - split trials into train / val / test WITHOUT leakage.
=================================================================
Standard library only (random).

THE GOLDEN RULE (spec rule #2):
  Split by WHOLE trial (a "group") FIRST. Only AFTER that do we cut
  windows. That way no little piece of a trial can appear in both the
  training set and the test set - which would be cheating.

`group_key` chooses how strict we are:
  "trial_id"  -> each recording is its own group (default)
  "config_id" -> every repeat of the same setting stays together (stricter)
"""

import random


def _group_of(trial, group_key):
    if group_key == "trial_id":
        return trial["trial_id"]
    if group_key == "config_id":
        return trial["config_id"]
    return trial["meta"][group_key]


def group_split(trials, ratios, seed=7, group_key="trial_id"):
    """
    Return a dict: {"train": [...], "val": [...], "test": [...]}.
    Whole groups go to exactly one set.
    """
    # 1. find the unique groups
    groups = []
    for t in trials:
        g = _group_of(t, group_key)
        if g not in groups:
            groups.append(g)

    # 2. shuffle the groups in a fixed, reproducible order
    groups = sorted(groups, key=str)          # stable starting order
    random.Random(seed).shuffle(groups)

    # 3. slice the group list by the ratios
    n = len(groups)
    n_train = int(n * ratios["train"])
    n_val = int(n * ratios["val"])
    train_groups = set(groups[:n_train])
    val_groups = set(groups[n_train:n_train + n_val])
    test_groups = set(groups[n_train + n_val:])   # the rest

    # 4. hand each trial to the set its group belongs to
    out = {"train": [], "val": [], "test": []}
    for t in trials:
        g = _group_of(t, group_key)
        if g in train_groups:
            out["train"].append(t)
        elif g in val_groups:
            out["val"].append(t)
        else:
            out["test"].append(t)

    return out


def assert_no_leakage(splits, group_key="trial_id"):
    """Crash loudly if the same group shows up in two sets. This is a GATE."""
    seen = {}
    for set_name in ("train", "val", "test"):
        for t in splits[set_name]:
            g = _group_of(t, group_key)
            if g in seen and seen[g] != set_name:
                raise AssertionError(
                    "LEAKAGE: group %r is in both %s and %s"
                    % (g, seen[g], set_name))
            seen[g] = set_name
    return True
