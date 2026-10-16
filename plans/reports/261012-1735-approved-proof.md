# Approved requirements and proof: validation, 2026-10-12

**Verdict: UNVERIFIED for native worker rollout.** Installed checks, macOS
subprocess write isolation and repository maintenance pass. Completed Claude
Code/Codex worker journeys and external-tool write restrictions were not observed.

Under test: branch `fix/approved-proof`, based on
`92ee775ffbdf08d05b246bbbdc88d758f28f932a`, with the working-tree changes for
issues #31, #36, #37 and #38. The oracle is the owner's requested fixes 1 and 2
and the [acceptance checklist](../../docs/approved-proof.md). No consumer app was
changed. All consumers/designs/builds/observations in these tests are synthetic.

Raw logs, coverage inputs/results and the tested plugin binding are retained at
`/Users/hugues_mini/huguesstack-evidence/2026-10-12-approved-proof-103514Z/`.
The filenames below are relative to that private evidence directory.

## Matrix

| Scenario/input | Required result | Observed result | Evidence |
|---|---|---|---|
| Builder replaces remembered filters with reset | Hold against approved original | PASS, exit 2 | `huguesstack-proof-unit-final.log`, changed-rules case |
| Approved file or source snapshot changes | Hold against trusted digest | PASS, exit 2 | Same log, changed-approval/source cases |
| Plugin/module changes after binding | Stop; changed code never executes | PASS, exit 2; sentinel absent | Same log, binding/runtime-drift cases |
| Worker writes allowed app path | Write succeeds within scope | PASS, file content inspected | Same log, worker scope case |
| Worker writes plugin, approval or binding; child/alias bypass | OS denies or preflight holds; bytes preserved | PASS on macOS | Same log, worker/alias/child/hardlink cases |
| Invalid write root, cwd or argv | No worker launch | PASS, exit 2 | Same log, invalid-worker case |
| Missing/empty/stale/unrelated/wrong-target proof | No supported pass | PASS, exit 2 | Same log, artifact/identity cases |
| Whole app build changes in resources | Old evidence cannot pass | PASS, exit 2 | Same log, whole-bundle case |
| Compressed prototype text, invalid/oversized input | Read text without execution; invalid data holds | PASS | Same log, bounded decode case |
| Readable PNG/JSON and matching inspected record | Accept consistent index | PASS, exit 0 | Same log, positive artifact cases; semantic meaning remains trusted inspection |
| Same declared verifier/builder, rejected or malformed receipt | No supported pass | PASS, exit 2 | `huguesstack-proof-review-red.log` then final suite |
| Crash plus missing artifact | Keep reported crash explicitly unaccepted | PASS, exit 2 with `accepted: false` | `huguesstack-proof-crash-red.log` then final suite |
| Missing attempt, blocked or owner-waived check | Distinct status; never passed | PASS | Final suite, unrun/no-attempt cases |
| Earlier failure then passing retry | Retain failure; require valid resolution receipt | PASS | Final suite, retry/reference/order cases |
| Unexplained data change or five open owner questions | Keep all supplied unresolved state; hold | PASS | Final suite, state/decision cases |
| New contract reachable in existing phases | Installed bound reads reach the guide | PASS | Final suite, workflow reach case |
| Original pstack names, phases, cardinalities and archives | Preserve existing contracts | PASS | Full suite and core/upstream logs |
| Completed native-host worker through protected consumer journey | Observe separately per host | UNVERIFIED | No native worker trial in this task |
| Remote MCP/IPC write restrictions | Observe equivalent host enforcement | UNVERIFIED; dependent use must hold | Process sandbox does not cover remote services |

## Suites and coverage

| Command | Result | Evidence |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | 427 passed, zero skipped, 103.520 seconds | `huguesstack-proof-unit-final.log` |
| `./scripts/check-plugin.sh` | PASS | `huguesstack-proof-plugin-final.log` |
| `python3 scripts/check_core.py` | PASS: 50 skills, 23 core/4 mobile playbooks, 2 agents, 15 roles | `huguesstack-proof-core-final.log` |
| `python3 scripts/upstream-diff.py check` | PASS: 161 upstream ledger rows | `huguesstack-proof-upstream-final.log` |
| `python3 scripts/check_whitespace.py` | PASS | `huguesstack-proof-whitespace-final.log` |
| Instrumented installed CLI tests, coverage 7.16.2 in temporary venv | 42 passed, zero skipped | `huguesstack-proof-coverage-tests.log` |

The 427 collected cases include one driver for 50 frozen historical cases;
do not add those children to the total. The 42 new cases execute installed
commands in external disposable consumers. No original assertion or frozen
archive was weakened to make them pass.

For the new runtime helper, 349/391 executable lines (89.3%) and 190/232 branches
(81.9%) ran. The bootstrap has 117/132 lines (88.6%) and 40/54 branches (74.1%).
Both exceed the testing skill's 80% line/70% branch defaults. The report and
instrumentation are retained in `huguesstack-proof-coverage.json`,
`huguesstack-proof-coverage-report.log` and the saved runner/config.

Uncovered runtime branches are mostly malformed-field/PNG rejection variants,
very large build limits, partial unreadable hold summaries and unavailable OS
enforcement. Existing plan/translation/audit branches also have full-suite
coverage outside this focused instrumentation. No line-coverage claim is made
for maintenance scripts. Coverage percentages do not authenticate approval or
prove artifact meaning. Non-macOS process isolation remains unobserved.

## Reproductions and corrections

The first tests failed because the public proof command did not exist. Further
red runs exposed blank/stale artifacts, guessed PNG
validity, malformed receipts and lost crash outcomes. The saved red logs record
those failures; the final suite exercises the corrected behavior.

For the review reproductions, change a synthetic accepted record's
`inspection.reference` to whitespace, or retain a failed attempt and set the
passing retry's `resolution_reference` to `true`. Both incorrectly returned
exit 0 before validation; they now return exit 2. Delete the artifact from a
record reporting a crash: the hold now retains that report as unaccepted.
Run `python3 -m unittest discover -s tests -p test_program_proof.py -v` to repeat
these cases from disposable clean state.

The initial full suite also caught the changed loader return shape and source
budget/receipt drift. Restore the original two-value interface, shorten repeated
pointers, retain the required phase-read wording and regenerate the reviewed
receipts. Those failures now pass. That initial run overlapped resealing for two
fixtures, which correctly rejected transient unapproved bytes; final runs used
the frozen payload. No green retry was used to dismiss an unexplained defect.

## Standards

The independent standards reviewer found malformed receipt references capable
of clearing a failure. After the public red reproduction and correction, its
recheck reported no remaining findings.

## Spec

The independent spec reviewer found the same receipt problem and the lost crash
on an invalid-proof hold. Its recheck confirmed both corrected through installed
commands, with no remaining findings or unsolicited scope expansion.

Review totals after corrections: Standards 0 unresolved; Spec 0 unresolved.

## Remaining rollout work

Run one small consumer journey separately in Claude Code and Codex with actual
host write restrictions and independently inspected tool receipts. Verify any
remote tool path before enabling its writes. Until then the contract must hold
dependent execution when enforcement is unavailable.

Keep current programs on their approved installation; migrating one requires
the owner's explicit approval of the new checklist/binding. Public names and
workflow order are preserved, while new-program pass conditions are stricter.
No push, PR, merge, release or issue closure was performed.
