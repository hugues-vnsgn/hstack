# Issue 29 investigation, 2026-10-13

**Verdict: UNVERIFIED for the reported workflow failure.** No remaining native
handoff violation was reproduced. The installed proof checks behaved as documented.
No production fix or native agent trial was performed.

## Scope and oracle

The approved scope is to follow existing pstack testing rules through task
handoff and completion checks, preserving reports and phase order. The selected
rule for further verification is the project's pre-review checks on the committed
head before a push starts a round. Later self-proof, CI and babysit may remain
parallel with swarm review after code-ready.

The command probe targets local fix/approved-proof at
f298d2ccef86f7ffb11cbb71f4e6c9d3abb52c72, including the earlier proof fixes.
The documentation branch feat/issue-29-spec is based on main
 e13a21a0658cf789f254995c9ba4ecdc7d2f00b2, which does not contain that local helper.
No production or collected test file in either checkout was changed.

## Matrix and observed results

| Scenario/input | Expected under the documented proof-command contract | Observed | Result |
|---|---|---|---|
| Valid synthetic indexed proof; project check only in a source snapshot | Evaluate indexed checks, with other workflow gates still independently required | Exit 0, ready:true | PASS for conditional proof scope |
| Same project check explicitly listed; no attempt | Hold missing check | Exit 2, ready:false, missing_proof contains C-PRE | PASS |
| Same listed check; actual fixture command exits 7 | Hold failed check | Exit 2, ready:false | PASS |
| Existing identity, missing-proof and retry regressions | Preserve earlier protection | 42/42 cases passed, zero skipped | PASS |
| Actual agent omits a due check and controller accepts that handoff | Drive and observe the real stage | Not performed; native trials are owner-deferred | UNVERIFIED |

The fixture uses synthetic build bytes, declared source/platform identities and
inspection receipts. It exercises record consistency, not Android behavior or a
real independent-verifier journey. The deliberately failing fixture command
actually ran and exited 7; it is not a consumer application defect.

## Re-runnable probe and evidence

Private evidence is under
/Users/hugues_mini/huguesstack-evidence/2026-10-13-issue-29/.
Run the repository diagnostic with the tested candidate:

    python3 plans/261013-1358-issue-29/probe.py --source /Users/hugues_mini/Codes/huguesStack.worktrees/fix/approved-proof --evidence /private/tmp/huguesstack-issue29-recheck

The expected diagnostic output is:

    project_check_exit: 7
    omitted_check_ready: true
    listed_unrun_check_ready: false
    listed_failed_check_ready: false

Fresh runs repeatedly produced those results. The first two took 0.353 and
0.450 seconds inside the fixture. Each run copied the plugin to an external
consumer directory with spaces and invoked its public bound CLI. The controlled
change was adding the project requirement to the approved/candidate index;
plugin code was unchanged.

Original command output, verdict JSON, the failed project-check log, binding and
source hashes are retained in the numbered evidence folders. The existing-suite
log records 42 cases in 18.215 seconds. The documentation-base full suite records
406 cases in 115.539 seconds, all passing with zero skipped. Their distinct
source revisions and test populations are not combined into a new total.

## Correction to the initial interpretation

The first scratch probe included an optional assertion that expected the
standalone proof command to enforce the unindexed project prerequisite. That
assertion failed. It imposed a broader duty than this API documents; it was not
a reproduction of an actual coding-agent handoff defect.

The spec reviewer identified this mistake. The raw reproduction.log and original
scratch probe are retained for transparency. The repository diagnostic removes
that unsupported assertion and checks only the documented behavior. No test was
weakened to make a production fix pass: no production fix exists, and no collected
regression test was added or changed.

The probe never observed requirement delivery or the controller's completion
decision. It therefore does not distinguish lost requirements, skipped required
commands, existing checks correctly holding the stage, or misuse of a partial
proof result. Those remain questions for actual workflow verification.

## Standards

The initial standards review reported zero findings. It confirmed fixture
isolation, raw result evidence and explicit native/mobile limits.
The recheck found incorrect shell continuation characters in the report's
command. The command is now one line and was executed successfully as written;
report-command.log records the result. No documented Standards findings remain.

## Spec

The initial spec review found one P2 overclaim: conditional proof readiness was
described as a demonstrated remaining workflow gap. This report and the revised
verification spec remove that claim and the presupposed implementation gate.
The follow-up review confirmed the correction and reported zero remaining
Spec findings, with pstack's timing and practical-test exception preserved.

## Recommendation and remaining proof

Review the [verification spec](../261013-1358-issue-29-spec.md). It requires actual
handoff and stage-decision evidence before proposing a fix. Keep #29 in
needs-triage pending the owner-deferred real trial.

No changed production-code coverage claim is made. No plugin skill, adapter,
public interface, archived source or collected unittest was modified. Passing
source checks and this diagnostic cannot establish native workflow support.
