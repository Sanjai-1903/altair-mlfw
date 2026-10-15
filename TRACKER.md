# ALTair - Master Tracker

Status key: TODO | WIP | BLOCKED | DONE
Update this file at every weekly review.

## Person 1 - Data & ML Baselines (P0-P2)  Owner: ______
| ID | Task | Phase | Status | Evidence file |
|----|------|-------|--------|---------------|
| A1 | Paper & data audit | P0 | TODO | docs/paper_audit.md |
| A2 | Data access & legal check | P0 | WIP  | data/manifests/access_ledger.csv |
| A3 | Dataset card + manifests | P0/P1 | WIP  | docs/data_card.md |
| A4 | Task charter & label ontology | P1 | TODO | decisions/task_charter.md |
| A5 | Group-safe splits + leakage tests | P1 | WIP  | data/splits/frozen_split.json |
| A6 | Baseline ladder B0-B3 | P2 | WIP  | experiments/reports/ |
| A7 | Run matrix + metrics framework | P2 | WIP  | experiments/index.csv |

## Person 2 - SNN & Fixed-Point Golden Model (P3-P4)  Owner: ______
| ID | Task | Phase | Status | Evidence file |
|----|------|-------|--------|---------------|
| B1 | SNN candidate families | P3 | TODO | experiments/reports/ |
| B2 | Mandatory parameter sweep | P3 | TODO | experiments/index.csv |
| B3 | Ablations & negative results | P3 | TODO | experiments/reports/ |
| B4 | Quantization contract | P4 | TODO | docs/model_card.md |
| B5 | Integer + C golden model | P4 | TODO | src/quant/, src/reference/ |
| B6 | Golden-vector package | P4 | TODO | export/golden_vectors/ |

## Person 3 - Firmware, Sizing & Verification (P5-P6)  Owner: ______
| ID | Task | Phase | Status | Evidence file |
|----|------|-------|--------|---------------|
| C1 | Telemetry input contract (FW1) | P5 | TODO | docs/interface_contract.md |
| C2 | Streaming & buffer owner (FW2) | P5 | TODO | src/firmware_ref/ |
| C3 | Reference preprocessing + loader (FW3-4) | P5 | TODO | src/firmware_ref/ |
| C4 | Driver, register map, packet (FW5-6) | P5 | TODO | docs/interface_contract.md |
| C5 | PC replay + self-tests (FW7-8) | P5 | TODO | tests/replay/ |
| C6 | Independent verification | G4/G6 | TODO | tests/numerical/ |
| C7 | Chip sizing + architecture handoff | P6 | TODO | docs/architecture_handoff.md |

## Gate status
| Gate | Must pass | Owner | Status |
|------|-----------|-------|--------|
| G0 | Data legal & source integrity verified | P1 | NOT PASSED |
| G1 | Valid labelled task exists (else off-nominal only) | P1 | NOT PASSED |
| G2 | Clean data contract, zero leakage | P1 | NOT PASSED |
| G3 | SNN justified vs matched baseline | P1+P2 | NOT PASSED |
| G4 | Bit-true, zero mismatches | P2+P3 | NOT PASSED |
| G5 | Firmware contract signed off | P3 | NOT PASSED |
| G6 | Architecture freeze, fits real hardware | P3+leads | NOT PASSED |

## A2 findings (2026-10-15) - access ledger v1 delivered
Evidence: data/manifests/access_ledger.csv  (4 sources audited)

Bottom line for Gate G1 (does a real fault-labelled task exist?):
- NO public source gives real rover motor/wheel FAULT labels.
- CAIDDA paper (S1): post-drive anomaly flagging only, no released data -> BLOCKED.
- RoSE-Lab (S2): best-fit telemetry (CC BY 4.0) BUT the S3 bucket does not
  exist yet (NoSuchBucket, verified 2026-10-15) - v0.7 prerelease, NOT
  downloadable today. Labels are terrain/settings only (off-nominal mobility,
  not faults). -> contact authors / wait for release.
- NASA PHM (S3): has run-to-failure labels, but for bearings/turbofan/
  batteries - NOT rover motors. Method reference only; do not conflate.
- Bench rig (S4): the ONLY route to real controlled fault labels, and it
  does not exist yet -> Task B is BLOCKED on a lead decision.

Provisional read (confirm against spec): ALTair is OFF-NOMINAL MOBILITY
detection (Task A) unless/until the bench rig is built. This matches the
task_charter consequence clause. Do NOT sign task_charter as Task B.

Outstanding before A2 can close (and G0 pass):
1. Spec .docx (ALT-MLFW-SPEC-001 Rev A) is MISSING - confirm each source
   name/URL/acronym against it (esp. 'CAIDDA').
2. RoSE-Lab S3 bucket confirmed ABSENT (not yet published) -> email
   bailey_hopkins@mines.edu for release/early access; no primary off-nominal
   dataset is in hand until then.
3. Record NASA PHM per-dataset citations (no formal licence stated).

## Build note (2026-10-15) - P1-P2 pipeline scaffold on SYNTHETIC data
Code delivered + tested on-device (python3 3.10, stdlib only, no installs):
  configs/  src/ingest  src/preprocessing  src/baseline  run_pipeline.py  tests/
Run:  python3 run_pipeline.py      |  python3 tests/run_all_tests.py  (3/3 pass)

Status: this is a HARNESS, not a result. All numbers come from synthetic
data and prove nothing (banner enforced in output + reports). A5 leakage
test and A6 baseline ladder (B0-B3) both run; A7 metrics framework
(precision/recall/F1/false-alarm-rate + false-alarms/hr) in place.

To switch to real data (when BK4 clears): drop real Processed_Data.csv
trials into data/processed/, set source: rose_lab in configs/dataset.yaml,
re-run. See docs/pipeline_howto.md.

Gates unchanged: G0-G6 still NOT PASSED (no real data yet). A3/A5/A6/A7
stay WIP until real data runs through the same code.
