# Task Charter  (P0.5 - owned by Project Lead)

Status: DRAFT - not signed. Must be signed by ML, Firmware and RTL leads.

## 1. Which task are we actually doing?
Mark ONE as primary. Do not mark Task B unless real fault labels exist.

- [ ] Task A - Unsupervised / one-class OFF-NOMINAL MOBILITY detection
      (terrain, slip, calibration, startup events). Supported by the paper.
- [ ] Task B - Controlled ACTUATOR LOAD/FRICTION FAULT detection
      Requires: our own bench rig with deliberately injected, physically
      measured conditions and valid labels. NOT available from the paper.

## 2. Three claims that must never be conflated
(A) Off-nominal mobility event detection.
(B) Controlled actuator abnormal-load/friction detection on a bench.
(C) Diagnosis of a physically degraded rover motor.
We may claim ONLY the level our actual data and test protocol validate.

Claim level we are permitted to make: ____________

## 3. Evidence backing this decision
| Question | Answer | Evidence |
|----------|--------|----------|
| Which datasets are confirmed accessible? | | data/manifests/ |
| Do ground-truth fault labels exist? | | |
| If no fault labels, is a bench rig feasible? | | |
| What generalization axes can we actually test? | | |

## 4. Consequence if Task B is not possible
Per Gate G1: do NOT build a supervised "motor failure" classifier.
Continue with correctly labelled off-nominal detection and open a
separate controlled fault-collection plan.

## 5. Signatures
| Role | Name | Date |
|------|------|------|
| ML training lead | | |
| Firmware lead | | |
| RTL / architecture lead | | |
| Verification lead | | |
