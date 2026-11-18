---
name: arena
description: "Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers into it. Use for /arena, 'arena this', 'throw it in the arena', or when one attempt at a non-trivial artifact would lock in the wrong shape."
disable-model-invocation: true
---

## Host invocation contract

Before tools, read [host contract](../../adapters/host.md)
and [mobile applicability](../../adapters/mobile.md#applicability) in full, then apply.
The host contract governs how this skill reaches any sibling dependency.

# Arena

Open a todolist with one entry per phase (Frame, Fan out, Cross-judge, Pick, Graft, Verify) before launching anything.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing.
2. Derive the rubric, 3-6 concrete gradeable criteria for what success looks like on *this* task. It is the picker's tool in Phase D. Candidates only see the task.
3. Pick the runners from the `arena runners` line in `.hstack/models.md`, one seat per entry, by default `claude-fable-5-2 high`, `claude-opus-5-5 high`, and `gpt-6-astra high`. If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, read the legacy file and tell the user to move it. An `inherit-parent` entry is the parent model, so omit `model` and spawn `generalPurpose`. Pass each entry's effort as the agent tool's effort setting. If the agent tool rejects an entry, run that seat on `inherit-parent` at the entry's effort and say so. Spawn more for multiple design directions, and repeat one model when the work is generation-bound, not judgment-sensitive. Pick each subagent's reasoning level for the job, per [workers and models](../../adapters/host-workers.md#model-defaults-and-role-labels).
4. Give each candidate its own output location (a git worktree where possible, otherwise `/tmp/arena-<slug>/candidate-<n>/`), per the **separate-before-serializing-shared-state** principle skill.

## Phase B: Fan out

Spawn all N subagents in one message with `run_in_background: true`, each with the task, the path to the shared grounding, its own output path, and instructions to produce the artifact and a short rationale naming the alternatives it considered and what it rejected.

If a candidate produces no output, proceed with N-1 and note the dropout.

## Phase C: Cross-judge

After all Phase B candidates complete, spawn one readonly judge from the `arena cross-judge pool` line in `.hstack/models.md`, by default `claude-opus-5-5 high`, `gpt-6-astra high`. The judge is never from the parent's vendor, and Fable counts as Claude for that check, so use the first entry from another vendor. When the host offers no other vendor's model, so that no entry qualifies, use the first entry whose model differs from the parent's and say that the vendor check fell back to a different model, so the judge is not skipped on that host. An `inherit-parent` entry is the parent model, so it never judges. If you do not know the parent's model, use the first real entry and say that the vendor check did not run. If the agent tool rejects an entry, use the next entry. If no entry runs, skip the judge, pick the base alone in Phase D, and say so. While you read in Phase D, the judge scores each candidate, by path label, on each rubric criterion and recommends a base.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or smaller API, per the Laziness Protocol.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate, not most of it. Fold each graft in by hand, per the **redesign-from-first-principles** principle skill, so the result stays coherent under one mental model. Don't paste mechanically.

If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If they wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Verify the synthesized artifact like any other output, per the **prove-it-works** principle skill. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Outputs

One synthesized artifact, with a short synthesis note alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.
