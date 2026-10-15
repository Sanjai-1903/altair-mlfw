# Architecture Freeze Sign-off

RELEASE RULE: if any item is unresolved, issue as PRE-FREEZE with
UNKNOWN/BLOCKED fields. A trained checkpoint alone does NOT freeze
the silicon architecture.

## Mandatory freeze checklist (no optional items)
- [ ] Target task and label ontology approved; motor-fault vs mobility-anomaly claim unambiguous
- [ ] Dataset rights, evidence, hashes and group-safe frozen splits approved
- [ ] Baselines B0, B1, B2 run; B3 if feasible; SNN sweeps completed fairly
- [ ] Held-out test evaluated ONCE under frozen selection, negative cases disclosed
- [ ] Exact topology, neuron dynamics, timesteps, encoding, output decision exported
- [ ] Quantization contract frozen; Python integer and C traces bit-identical
- [ ] Immutable weights, normalizers, thresholds and golden vectors delivered
- [ ] Firmware stream/driver/register and recovery semantics signed off
- [ ] GF180 memory, cycle, IO, area and clock feasibility reviewed vs actual macros
- [ ] NPU keep/remove and DSP add/no-add decisions justified, not assumed
- [ ] Independent clean rebuild and signed review evidence archived

## Approval block
Freeze is NOT effective until independent evidence review passes.

| Approver | Name / date | Status / evidence link |
|----------|-------------|------------------------|
| ML training lead | | |
| Firmware lead | | |
| RTL / architecture lead | | |
| Verification / physical design lead | | |

Test package hash: ____________    Revision: ____________
Outstanding exceptions: ____________
