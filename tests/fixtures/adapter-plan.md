# Program

## How to read this
One box is one unit of work and names the evidence.
Check a box only when its evidence exists. Read playbooks/.
Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

## Program checklist
### Arm the program
`git show origin/main:PLAN.md`
`git show origin/main:skills/hugues-mode/playbooks/feature.md`
`node pstack/skills/poteto-mode/scripts/check-plan.mjs plan.md`
### Spawn owners
/loop 1h
### PR mechanics
status message
### Verdict and merge
### Boot recipe

## PR 1
**Depends on.** None.
**Files.**
- [ ] file.py
**Build.**
- [ ] Build succeeds.
**You see.**
- [ ] Observable behavior.
**Verify, unit.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.
- [ ] Regression passes.
**Verify, live.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked. Ten lanes on `inherit-parent` at the PR head
- [ ] Lane 1. Drive. Save `lane-1.png`. Pass when visible.
- [ ] Lane 2. Drive. Save `lane-2.png`. Pass when visible.
- [ ] Lane 3. Drive. Save `lane-3.png`. Pass when visible.
- [ ] Lane 4. Drive. Save `lane-4.png`. Pass when visible.
- [ ] Lane 5. Drive. Save `lane-5.png`. Pass when visible.
- [ ] Lane 6. Drive. Save `lane-6.png`. Pass when visible.
- [ ] Lane 7. Drive. Save `lane-7.png`. Pass when visible.
- [ ] Lane 8. Drive. Save `lane-8.png`. Pass when visible.
- [ ] Lane 9. Drive. Save `lane-9.png`. Pass when visible.
- [ ] Lane 10. Drive. Save `lane-10.png`. Pass when visible.
**Verify, perf.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.
- [ ] Metric. latency
- [ ] Probe. local probe
- [ ] Baseline. old revision
- [ ] Rule. no regression
**Review gate.** None.
**Merge.**
- [ ] Authorized merge.

## Close the program
## Appendix Prototype evidence
