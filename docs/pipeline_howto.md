# How the P1->P2 pipeline works (read me before the code)

**Everything here runs on SYNTHETIC data.** No result from it may be
used as a claim. It exists so the pipeline is built and tested *now*,
before the real RoSE-Lab data is available (see
`data/manifests/access_ledger.csv`).

## Run it

```bash
python3 run_pipeline.py          # make data (if needed) + score baselines
python3 run_pipeline.py --regen  # regenerate data from scratch
python3 tests/run_all_tests.py   # schema + no-leakage + determinism
```

No installs. Standard-library Python only.

## The pieces (in order)

| Step | File | What it does |
|------|------|--------------|
| 1 | `configs/dataset.yaml` | names the signals and the label; `source:` flips synthetic -> real |
| 2 | `src/ingest/synth.py` | makes fake telemetry with the REAL column names |
| 3 | `src/ingest/load.py` | reads trials back into memory |
| 4 | `src/preprocessing/splits.py` | splits **by whole trial first** + proves no leakage |
| 5 | `src/preprocessing/windows.py` | cuts windows (AFTER the split) + simple features |
| 6 | `src/baseline/baselines.py` | the B0-B3 "can you beat this?" ladder |
| 7 | `src/baseline/metrics.py` | precision / recall / F1 / false-alarm rate |
| 8 | `run_pipeline.py` | ties it together, opens TEST once, writes a report |

## The three rules, enforced in code

1. **Honesty** - the report prints the best baseline and says the SNN
   must beat it or it is NO-GO. The label is called *off-nominal
   mobility*, never *fault*.
2. **No leakage** - `assert_no_leakage()` crashes if one trial reaches
   two sets. Windows are made only after the split. Test is opened once.
3. **Reproducible** - fixed seeds; `test_determinism.py` checks a repeat
   run is identical. (Full bit-exact integer/C work comes later, in P4.)

## When the real data arrives

1. Put the real `Processed_Data.csv` trials under `data/processed/`
   (or point `processed_dir` at them) and write a real `_trials_index.csv`.
2. Change `source: synthetic` -> `source: rose_lab` in `dataset.yaml`.
3. Re-run. If the column names match, nothing else changes.

## What is NOT here yet (on purpose)

- The SNN (phase P3) - not allowed until baselines + real data exist.
- Quantization / bit-exact integer + C model (phase P4).
- Firmware / GF180 sizing (phases P5-P6).
