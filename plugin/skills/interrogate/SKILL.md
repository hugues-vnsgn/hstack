---
name: interrogate
description: "Use for \"interrogate\", \"adversarial review\", \"multi-model review\", \"challenge this\", \"stress test this code\", \"find blind spots\", or \"tear this apart\". Adversaries try to break a change or design, and only findings proven by a run survive."
disable-model-invocation: true
---

## Host invocation contract

Before tools, read [host contract](../../adapters/host.md)
and [mobile applicability](../../adapters/mobile.md#applicability) in full, then apply.
The host contract governs how this skill reaches any sibling dependency.

# Interrogate

Adversaries try to break a change or a design. A finding survives only when a run proves it. Report the findings. Do not apply fixes.

## Frame

The scope is what the user names. Otherwise it is the branch diff from its merge base with the base branch, through the working tree. State the intent with the **in-your-own-words** skill, from the user's message, the commits, and the PR description. Ask the user when the intent is unclear.

## Fan out

Run Phase A steps 3 and 4 and Phase B of the **arena** skill, with four changes. Read the `interrogate reviewers` line in `.hstack/models.md` in place of `arena runners`. If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, read the legacy file and tell the user to move it. Copy the scope's uncommitted changes into each worktree. Spawn each adversary as `generalPurpose`. In place of the arena task and rationale, give each adversary the scope, the intent, and this brief:

> Break this change. Prove each finding with a run against the real code, such as a failing test, a repro script, or command output that shows the wrong behavior. For a design or plan, run a prototype or probe the current tree. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run. That covers style, naming, structure, and risks that need a future change to matter. No findings is a valid result.

Add the language baselines to each brief: absolute installed paths matching the
languages in the scope, or `none`, each read in full before the first source read. Use
`<plugin>/skills/swift-best-practices/SKILL.md` for Swift and
`<plugin>/skills/kotlin-best-practices/SKILL.md` for Kotlin. Resolve `<plugin>`
from the loaded mode path through [workflow tools](../../adapters/host-workflow-tools.md).
Include both paths for mixed-language work. When the caller names a review lens, such as the
mobile review lens, add it to each brief too.

## Verify

Verify each finding per arena Phase F by rerunning its command. Keep a finding when the output shows the failure and the failure breaks the intent. Drop the rest. Merge findings that share a root cause.

Skip arena Phases C, D, and E. Adversaries find different failures, so the verdict keeps every verified finding, not one adversary's list.

## Output

- **Intent**: the restatement.
- **Findings**: for each verified finding, the command, its output, how it breaks the intent, and the adversaries that found it. Say "no verified findings" when none survive.
- **Dropped**: for each adversary, the count of dropped findings and why.
