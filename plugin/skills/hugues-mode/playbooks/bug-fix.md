### Bug fix

**You own this task. Plan, review, verify.** Delegate investigation and the fix to subagents, stay in the lead. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section.

Be scientific. Every shipped line traces to runtime evidence. Belt-and-suspenders that "might help" is a hypothesis, not a fix. It does not ship. When evidence refutes a hypothesis, revert what it motivated. The smallest change the evidence justifies ships, nothing more.

1. Reproduce it yourself on the matching surface via the control skill (Non-negotiables), even when a debug or instrumentation protocol says to ask the user to reproduce. Ask the user only with a stated, specific reason the control surface cannot reach the target, and only after driving it as far as it goes. If it won't reproduce directly, synthesize the trigger, tighten conditions, or instrument until it fires.
2. Binary-search the cause. Form the candidate hypotheses, then rule them out until one survives. Seed them with `how` over the affected subsystem and the **why** skill for regression history. Each pass, take the split that cuts the most remaining problem space, get runtime evidence, eliminate. When program state is unclear, add instrumentation or logging and read it as the code runs. Don't guess. Drive a long or stubborn hunt with Cursor's `/loop` command. Confirm the surviving *mechanism* with runtime evidence before the step-3 architect/interrogate fan-out.
3. Plan the fix. If it crosses a function boundary, `architect` first. Delegate implementation to a subagent using your configured bug-fix model (default `inherit-parent xhigh`) with a specific scope.
4. Verify on the same surface. The original repro now passes. "Inconclusive" or wrong-surface is not a pass. Flag it. Unit tests show branch behavior, not bug absence.
5. Stage the commits so the failing repro lands before the fix in git history. See the **tdd** skill for the failing-test-first cadence when the bug has a cheap local test path. Skip it when the test would be expensive, integration-heavy, or unclear.
   This is the canonical **sequence-verifiable-units** principle skill, the failing test first and the fix on top.

   For mobile bugs, retain the adapter's separate regression and production workers.
   Use a fresh general-purpose regression worker. It reads only the `tdd` SKILL.md,
   the matching language baseline at absolute installed paths, and the files named
   in its brief. It does not load the full mode or principles. The production worker is unchanged.
   Put this contract in the regression brief. It overrides transitive skill reads
   and TDD's production-edit steps.
   The coordinator never writes the regression test. On a stall, dispatch one fresh
   replacement with a narrower brief. A second stall marks the regression step
   blocked. State it in the final message.
   Run the same selected regression through the [native execution helper](../../../adapters/native-execution.md)
   before the production change and afterward. Independently inspect RED and GREEN,
   actual counts and the retained native reports. If automated testing is impractical,
   record the concrete reason and executable runtime reproduction without claiming
   automated RED/GREEN. Original runtime proof and the final consumer recipe remain required.
6. Run **Opening a PR**. For explicitly selected mobile work, run **interrogate** with the [mobile review lens](../references/mobile-review.md) in this step, even when you open the PR yourself. Reuse this review when Opening a PR already requires `interrogate`.

**Reply:** what was broken, root cause, fix, how you verified. Paste failing-then-passing repro output verbatim.
