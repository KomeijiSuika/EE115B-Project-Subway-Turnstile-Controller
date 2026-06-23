# Audit Report — Subway Turnstile Controller

**Date**: 2026-05-27
**Phase**: lifecycle_init
**Tooling**: Icarus Verilog 11.0, GTKWave, Graphviz 12.2.1, Python 3.13 (ReportLab)

---

## Overall Verdict: ALL PASS ✅

All five simulations compile and run successfully. VCD waveform verification confirms correct FSM behavior for every part.

---

## Per-Part Audit

### Part 1 — Two-State Turnstile (20 pts)

| Check | Result | Detail |
|---|---|---|
| Compile | PASS | iverilog: no errors |
| Simulate | PASS | vvp: clean finish |
| FSM Correctness | PASS | LOCKED ↔ UNLOCKED transitions confirmed via VCD |
| Reset | PASS | Asynchronous active-low reset to LOCKED |
| Outputs | PASS | gate_open/led_green/led_red correct per state |
| Testbench | PASS | Provided testbench covers 1 full passage cycle |

**Verdict: 20/20** — No issues found.

---

### Part 2 — Basic Access Control (20 pts)

| Check | Result | Detail |
|---|---|---|
| Compile | PASS | iverilog: no errors |
| Simulate | PASS | vvp: clean finish |
| FSM Correctness | PASS | IDLE→VALID→PASS→CLOSE→IDLE chain verified |
| sensor_A ignored in IDLE | PASS | Confirmed: gate stays closed when sensor_A=1 in IDLE |
| card_valid ignored in non-IDLE | ✅ | Structural: next_state only checks card_valid in IDLE |
| CLOSE→IDLE on sensor_B=0 | PASS | Confirmed transition in VCD |
| Testbench | PASS | Student-written; covers both edge cases |
| Signal Interface | PASS | clk, rst_n, card_valid, sensor_A, sensor_B, gate_open, led_green, led_red |

**Verdict: 20/20** — Student testbench well-written and comprehensive.

---

### Part 3 — Reverse Intrusion Detection (20 pts)

| Check | Result | Detail |
|---|---|---|
| Compile | PASS | iverilog: no errors |
| Simulate | PASS | vvp: clean finish |
| ALARM state | PASS | sensor_B in IDLE triggers ALARM (priority) |
| Alarm Duration | PASS | 10 clock cycles (ALARM_DURATION=10, confirmed via VCD) |
| Gate during ALARM | PASS | gate_open=0, led_red=1 throughout |
| card_valid priority | PASS | sensor_B > card_valid in IDLE |
| Parameter usage | PASS | ALARM_DURATION as parameter (not hardcoded) |
| Alarm counter reset | PASS | Resets properly on exit from ALARM |

**Verdict: 20/20** — Correct priority-based reverse intrusion detection.

---

### Part 4 — Timeout Auto-Close (20 pts)

| Check | Result | Detail |
|---|---|---|
| Compile (4a) | PASS | iverilog: no errors |
| Compile (4b) | PASS | iverilog: no errors |
| Simulate (4a) | PASS | Timeout case: gate closes at 10 cycles |
| Simulate (4b) | PASS | Normal case: no alarm, no timeout |
| TIMEOUT state | PASS | VALID→TIMEOUT after TIMEOUT_DURATION=10 |
| PASS_ALARM state | PASS | Gate open, alarm=1, waits for sensor_B |
| Parameter usage | PASS | TIMEOUT_DURATION as parameter |
| Testbench (4a) | PASS | Student-written timeout case |
| Testbench (4b) | PASS | Student-written normal passage case |
| ALARM retained | PASS | Part 3 alarm logic preserved |

**Verdict: 20/20** — Most feature-complete controller. Both student testbenches correctly verify timeout and normal passage.

---

### Report — report.pdf (20 pts)

| Check | Before | After |
|---|---|---|
| FSM diagrams | ✅ Graphviz DOT for all 4 parts | ✅ (unchanged) |
| Simulation waveforms | ✅ VCD-rendered PNGs for all parts | ✅ (unchanged) |
| Student info | ✅ Name + ID on title page | ✅ (unchanged) |
| Per-part verification | ⚠️ Missing | ✅ Added compile/simulate/behavior check |
| Conclusion summary | ⚠️ Missing | ✅ Added results table + feature list |
| Signal reference | ⚠️ None | ✅ Verification text references key signals |

**Improvements applied**:
- Added per-part verification status (Compile/Simulate/Behavior)
- Added conclusion with summary results table (all 4 parts)
- Added key design features bullet list
- Added submission checklist
- Improved typography consistency

**Verdict: 20/20** — Original report was already good; optimization adds structured verification and conclusion.

---

## Grade Summary

| Component | Score | Status |
|---|---|---|
| Part 1 | 20 | PASS |
| Part 2 | 20 | PASS |
| Part 3 | 20 | PASS |
| Part 4 | 20 | PASS |
| Report | 20 | PASS |
| **Total** | **100** | **ALL PASS** |
