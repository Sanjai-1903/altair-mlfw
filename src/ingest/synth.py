"""
synth.py - make FAKE rover telemetry that looks like the real thing.
==================================================================
Standard library only (random, math, csv). No numpy needed.

WHY: the real RoSE-Lab dataset is not downloadable yet (see
data/manifests/access_ledger.csv). So we build the whole pipeline on
synthetic data that has the SAME COLUMN NAMES and shape as the real
Processed_Data.csv. The day real data arrives, the rest of the code
does not change.

HONESTY: every value here is invented. The label `is_off_nominal`
is a synthetic OFF-NOMINAL MOBILITY event (like a wheel slipping or
briefly stalling). It is NOT a real mechanical motor fault.

Each trial is written as one CSV: data/processed/trial_XXXX.csv
A master list is written to:   data/processed/_trials_index.csv
"""

import os
import csv
import math
import random

# These MUST match configs/dataset.yaml feature_columns (same order).
FEATURES = [
    "current1", "current2", "current3", "current4",
    "vel1_rad_s", "vel2_rad_s", "vel3_rad_s", "vel4_rad_s",
    "ang_vel_x", "ang_vel_y", "ang_vel_z",
    "lin_acc_x", "lin_acc_y", "lin_acc_z",
]
COLUMNS = ["time_s"] + FEATURES

SAMPLE_RATE_HZ = 50


def _one_trial(rng, speed_cmps, inclination_deg, make_off_nominal):
    """Build the time series for a single trial. Returns a list of rows."""
    # how long this trial lasts (seconds) -> number of samples
    duration_s = rng.uniform(8.0, 15.0)
    n = int(duration_s * SAMPLE_RATE_HZ)

    # base wheel speed (rad/s) is proportional to commanded linear speed
    base_vel = 0.3 * speed_cmps                 # simple made-up relation
    # going uphill costs more current; +incline = uphill
    incline_load = 0.05 * inclination_deg

    # if this trial is off-nominal, pick ONE wheel to misbehave and when
    bad_wheel = rng.randint(0, 3) if make_off_nominal else -1
    bad_start = rng.randint(int(n * 0.3), int(n * 0.6)) if make_off_nominal else n
    bad_len = rng.randint(int(n * 0.1), int(n * 0.25)) if make_off_nominal else 0

    rows = []
    for i in range(n):
        t = i / SAMPLE_RATE_HZ
        row = {"time_s": round(t, 4)}

        # ---- four wheels: velocity and current ----
        for w in range(4):
            vel = base_vel + rng.gauss(0, 0.05)        # small jitter
            cur = 2.0 + 0.8 * abs(vel) + incline_load + rng.gauss(0, 0.1)

            # inject the synthetic off-nominal pattern on the bad wheel:
            # wheel slows down (loses grip / jams) while current spikes.
            if w == bad_wheel and bad_start <= i < bad_start + bad_len:
                vel = vel * 0.2                        # wheel nearly stalls
                cur = cur * 2.5 + rng.gauss(0, 0.3)    # current jumps

            row["vel%d_rad_s" % (w + 1)] = round(vel, 5)
            row["current%d" % (w + 1)] = round(cur, 5)

        # ---- IMU: angular velocity (rad/s) and linear acceleration (m/s^2)
        row["ang_vel_x"] = round(rng.gauss(0, 0.02), 5)
        row["ang_vel_y"] = round(rng.gauss(0, 0.02), 5)
        row["ang_vel_z"] = round(rng.gauss(0, 0.03), 5)
        # gravity component along the slope + noise
        g_along = 9.81 * math.sin(math.radians(inclination_deg))
        row["lin_acc_x"] = round(g_along + rng.gauss(0, 0.05), 5)
        row["lin_acc_y"] = round(rng.gauss(0, 0.05), 5)
        row["lin_acc_z"] = round(9.81 + rng.gauss(0, 0.05), 5)

        rows.append(row)
    return rows


def generate_dataset(out_dir="data/processed",
                     n_configs=12, trials_per_config=8,
                     off_nominal_fraction=0.22, seed=7):
    """
    Generate the whole synthetic dataset.
    Returns the list of trial-metadata dicts (also written to _trials_index.csv).
    """
    os.makedirs(out_dir, exist_ok=True)
    rng = random.Random(seed)

    # the experimental settings, like RoSE's Speed_Radius_Direction_Inclination
    speeds = [1, 3, 5, 7, 10]            # cm/s
    radii = [0, 60, 120]                 # cm (0 = spin in place)
    directions = ["Left", "Right"]
    inclinations = [-30, -15, 0, 15, 30]  # degrees

    index = []
    trial_id = 0
    for c in range(n_configs):
        speed = rng.choice(speeds)
        radius = rng.choice(radii)
        direction = rng.choice(directions)
        incline = rng.choice(inclinations)
        config_id = "%d_%d_%s_%d" % (speed, radius, direction, incline)

        for _ in range(trials_per_config):
            # each trial gets its own seeded rng so runs are reproducible
            trial_rng = random.Random(seed * 100000 + trial_id)
            is_off = 1 if trial_rng.random() < off_nominal_fraction else 0

            rows = _one_trial(trial_rng, speed, incline, is_off == 1)

            csv_name = "trial_%04d.csv" % trial_id
            csv_path = os.path.join(out_dir, csv_name)
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerows(rows)

            index.append({
                "trial_id": trial_id,
                "config_id": config_id,
                "speed_cmps": speed,
                "radius_cm": radius,
                "direction": direction,
                "inclination_deg": incline,
                "is_off_nominal": is_off,
                "n_samples": len(rows),
                "csv_path": csv_name,
            })
            trial_id += 1

    # write the master index
    index_path = os.path.join(out_dir, "_trials_index.csv")
    with open(index_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(index[0].keys()))
        writer.writeheader()
        writer.writerows(index)

    return index


if __name__ == "__main__":
    data = generate_dataset()
    n_off = sum(t["is_off_nominal"] for t in data)
    print("SYNTHETIC DATA - not for any claim")
    print("generated %d trials (%d off-nominal) in data/processed/"
          % (len(data), n_off))
