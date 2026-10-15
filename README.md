# ALTair-MLFW

Neural architecture & reproducible software baseline.
Rover mobility anomaly detection | GF180 research ASIC.

Spec: ALT-MLFW-SPEC-001 Rev A.

## Status
PRE-FREEZE. No neural topology, accuracy, quantization or silicon
efficiency claim is approved yet.

## Three rules
1. Scientific honesty - claim only what the data proves.
2. No data leakage - split by whole drive/session, test set opened once.
3. Bit-exact - Python integer model and C reference must match exactly.

## Team split (3 people)
- Person 1  Data & ML baselines       Phases P0-P2  Gates G0,G1,G2
- Person 2  SNN & fixed-point model   Phases P3-P4  Gates G3,G4
- Person 3  Firmware, sizing, verify  Phases P5-P6  Gates G5,G6

## Layout
data/        manifests, raw (ignored), processed, splits
src/         ingest, preprocessing, baseline, snn, quant, reference, firmware_ref
configs/     dataset.yaml, splits.yaml, model_search.yaml, inference.yaml
experiments/ index.csv, reports, plots, frozen_runs
export/      model_package, weights, metadata, golden_vectors
tests/       unit, data_contract, determinism, numerical, replay
docs/        data_card, model_card, interface_contract, architecture_handoff
decisions/   ADR-*, freeze_signoff.md, blockers.md

## Reproduce
    make reproduce RUN=<frozen_run_id>
