# ALTair - Start Here

Read this first. It tells you what the project is, where we are now,
and what to do next. Written for someone joining cold.

---

## 1. What we are building (plain words)

A rover's wheels and motors produce sensor data: current, voltage, wheel
speed, commanded motion, IMU. We want to automatically spot when that
behaviour goes OFF-NOMINAL - something is not right.

The twist: it must eventually run on a small custom chip (GF180 research
ASIC), not a laptop. So we are looking for the SMALLEST defensible
neural network that does the job - and we are specifically testing
whether a Spiking Neural Network (SNN) is worth the extra complexity.

The real deliverable is not "a model". It is a complete, reproducible
evidence package that lets chip engineers size memory, cycles, and area
with confidence.

---

## 2. The three rules (non-negotiable)

1. SCIENTIFIC HONESTY
   Claim only what the data proves. If a simple threshold rule beats
   the SNN, say so and recommend NO-GO. A nice accuracy number alone
   is explicitly not acceptable.

2. NO DATA LEAKAGE
   Split by whole drives/sessions FIRST, then make windows. The test
   set is opened exactly once, at the end. Nothing from test may touch
   training, normalization or threshold setting.

3. BIT-EXACT
   The final integer math must match perfectly: Python integer model
   == C reference == (later) RTL. Zero mismatches. Not "close enough".

Everything is versioned with git commits and SHA-256 checksums.
Anything that cannot be rebuilt on a second clean machine is NOT frozen.

---

## 3. The flow

P0  Get legit data        -> Gate G0/G1  data legal + real task exists
P1  Clean & split data    -> Gate G2     zero leakage
P2  Prove simple methods  ->             sets the bar for the SNN
P3  Build the SNN         -> Gate G3     SNN justified vs baseline
P4  Freeze exact math     -> Gate G4     bit-true, zero mismatches
P5  Wrap in firmware      -> Gate G5     firmware contract signed
P6  Hand off to chip team -> Gate G6     architecture freeze

Nothing freezes on a guess. Nothing freezes if a simpler method wins.

---

## 4. Who does what (3 people)

Person 1  Data & ML baselines        P0-P2   tasks A1-A7
Person 2  SNN & fixed-point model    P3-P4   tasks B1-B6
Person 3  Firmware, sizing, verify   P5-P6   tasks C1-C7

Project lead holds scope, decisions and final signatures on top.
Full detail: ALTair_Team_Work_Split_3People.pdf (in the CDG folder).
Live status: TRACKER.md

Handoffs:
  P1 -> P2   frozen splits + deployable signal list + which task is valid
  P2 -> P3   quantization contract + golden vectors
  P3 -> P2   independent replay; any mismatch bounces back before freeze
  P3 -> chip memory / cycle / area numbers vs real GF180 macros

---

## 5. Where we are RIGHT NOW

Status: PRE-FREEZE. Nothing approved. No data audited yet.

Done:
  [x] Repo created with the mandatory layout
  [x] Tracker, task charter stub, weekly review, freeze checklist
  [x] 3-person work split agreed

Not started:
  [ ] Everything in P0 onwards

All gates G0-G6: NOT PASSED.

---

## 6. What happens next (immediate)

1. Assign names to Person 1 / 2 / 3 in TRACKER.md
2. Person 1 starts A1 (paper audit) and A2 (what data can we actually
   download and legally use?) - this is the critical path
3. Project lead drafts decisions/task_charter.md but does NOT sign it
   until A2 comes back with real answers

---

## 7. The biggest risk, up front

We may not have real motor-fault labels.

The reference paper studies post-drive anomaly flagging - it is NOT a
public, verified, fault-labelled training dataset. If no ground-truth
fault labels exist, Gate G1 forbids building a supervised "motor
failure" classifier. The project then becomes off-nominal mobility
detection only, plus a separate controlled bench-collection plan.

Find this out in week 1, not week 5.

Other live risks: dataset leakage, high false-alarm burden on normal
terrain, SNN offering no benefit over a simple baseline, quantization
collapsing accuracy, model not fitting real GF180 memory.

---

## 8. Things we must never do

- Claim NASA endorsement, or use a NASA name to imply it
- Claim exact reproduction of the paper without its original data+code
- Treat normal slip / rock impact / calibration / terrain load as
  mechanical degradation
- Commit raw proprietary telemetry or restricted data to the repo
- Invent register addresses before the RTL team approves them
- Freeze 256 SNN neurons just because existing RTL has that number
- Report a best-seed-only result

---

## 9. Key files

CONTEXT.md                    this file
TRACKER.md                    live status of every task + gate
decisions/task_charter.md     which task we are allowed to claim
decisions/blockers.md         anything BLOCKED
decisions/freeze_signoff.md   final checklist + signatures
docs/weekly_review.md         the 5 questions, every week
docs/data_card.md             data sources, rights, provenance
docs/model_card.md            model, limits, metrics
docs/interface_contract.md    firmware/hardware interface
docs/architecture_handoff.md  memory, cycles, area for the chip team

Spec of record: ALT-MLFW-SPEC-001 Rev A
