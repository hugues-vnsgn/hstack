---
name: setup-huguesstack
description: Configure huguesStack's model and reasoning budget per role. Use when setting up huguesStack or changing which models it uses.
---

## Host invocation contract

Before these workflow steps, apply the [host contract](../../adapters/host.md)
and [mobile applicability](../../adapters/mobile.md#applicability).
The host contract governs how this skill reaches any sibling dependency.

# Setup pstack

Write `.huguesstack/models.md` at the project root: the model-role file every pstack skill reads before it picks a worker's model.

## Role values

A role value is one or more alternatives joined by ` or `, such as `opus high or gpt-6-astra high`. Each alternative is a model and an effort.

- The model is `inherit-parent` or a real slug, a value a host's native agent tool accepts for `model`: a Claude Code alias such as `opus` or `sonnet`, or a Codex model such as `gpt-6.1-sol`. `inherit-parent` leaves `model` unset, so the worker runs on the parent chat model. It is valid on every host.
- The effort is the last token, on the ladder `max` > `xhigh` > `high` > `medium` > `low`. It sets the agent tool's effort.
- A host runs the first alternative its agent tool accepts, so one file serves both hosts: a single-model role lists its Claude model first and its Codex model after it. With no accepted alternative, the role runs on `inherit-parent` at the first alternative's effort.
- A panel role (arena runners, architect runners, interrogate reviewers) holds a comma-separated list, and one subagent runs per entry, `inherit-parent` entries included, so the list length sets the count. Give each seat a model for both hosts and alternate which comes first, to use distinct available models where possible: `opus xhigh or gpt-6-astra xhigh, gpt-6.1-sol xhigh or sonnet xhigh` runs Opus against Sonnet in Claude Code and GPT-6-Astra against GPT-6.1-Sol in Codex. Distinct models give model diversity; a repeated model gives process independence.
- `arena cross-judge pool` is also a list, but Arena selects one value from it whose model differs from the parent's when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

## Model tiers

Step 5 gives each role a tier. When a host's model list changes, keep the tier and map it to that host's current model.

| Tier | Claude Code | Codex | Roles |
|---|---|---|---|
| Workhorse | `sonnet` | `gpt-6.1-sol` | Code delegates, explorers, investigators, reflect tooling, swarm workers |
| Judgment | `opus` | `gpt-6-astra` | Judgment and prose, explainer, synthesizers, reflect reviewers |
| Frontier | `fable` | `gpt-6-astra` at `xhigh` | Hardest tasks, one design or review seat, the cross-judge |

Effort follows the work: `medium` for parallel reading, lanes and hillclimb iterations, `high` for scoped implementation and judgment, `xhigh` for fixes, design and adversarial review.

## Steps

### 1. Detect available models

Read the `model` and effort values your host's native agent tool accepts from its own schema in this session. In Claude Code that is the Agent tool's `model` enum (aliases such as `opus` or `sonnet`) and its `effort` enum. When the schema offers no model choice, the detected set is empty and every role stays on `inherit-parent`. Never write a real slug you have not confirmed is available, except the other host's alternatives, which step 4 lists as unverified.

### 2. Load current state

The starting role values are the file shape shown in step 5 below. If `.huguesstack/models.md` already exists, read it and treat its `# budget` line and its role values as the current choices. Otherwise start from those values. A line whose role is not in step 5, such as `how critics`, is from a retired role. Drop it.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Prefer AskQuestion over free text. Offer these four options with these exact labels, and name the current budget when the file records one.

- `unlimited — keep max`
- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) Apply it.** Build the working table from the step 5 values, and on a re-run keep the models or list of any role whose value differs from its step 5 value. `unlimited` leaves every effort as in that table. `large`, `medium`, and `small` set the effort of every alternative, panel and `inherit-parent` entries included, to `xhigh`, `high`, or `medium`. If the agent tool does not accept that effort for that model, use its highest accepted effort below the target, else mark the role as needing a choice. So `small` turns `opus xhigh or gpt-6-astra xhigh` into `opus medium or gpt-6-astra medium`.

**(c) Show the roles and confirm.** Show every role with its value, marking any current-host slug not in the detected set as needing a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models plus `inherit-parent` as the options. Prefer AskQuestion over free text.

### 4. Validate

Every real slug written for the current host must be in the detected set. The other host's alternatives (Codex models when setup runs in Claude Code, Claude aliases when it runs in Codex) cannot be confirmed here: keep them and list them as unverified. `inherit-parent` always passes. If a chosen real slug is not available, stop and ask again.

### 5. Write the file

Write `.huguesstack/models.md` with a `# budget` line naming the chosen label and its target effort, and one line per role, using the role labels in [workers and models](../../adapters/host-workers.md#model-defaults-and-role-labels). Overwrite the whole file so re-runs stay idempotent. Shape:

```
# huguesStack model roles. One line per role. Delete a line to fall back to the skill default (`inherit-parent`).
# Value: alternatives joined by ` or `, each `<model> <effort>`. A host runs the first one its agent tool accepts. Panel seats alternate which host's model comes first. `inherit-parent` leaves the agent tool's `model` unset. Each comma-separated panel entry runs one subagent.
# budget: unlimited (max)
feature, refactoring: sonnet high or gpt-6.1-sol high
bug-fix: sonnet xhigh or gpt-6.1-sol xhigh
perf-issue: sonnet xhigh or gpt-6.1-sol xhigh
hillclimb: sonnet medium or gpt-6.1-sol medium
judgment and prose: opus high or gpt-6-astra high
hardest tasks: fable xhigh or opus max or gpt-6-astra xhigh
how explorer: sonnet medium or gpt-6.1-sol medium
how explainer: opus high or gpt-6-astra high
why investigators: sonnet high or gpt-6.1-sol high
why synthesizer: opus xhigh or gpt-6-astra xhigh
reflect tooling: sonnet high or gpt-6.1-sol high
reflect judgment, divergent, synthesizer: opus high or gpt-6-astra high
arena runners: opus xhigh or gpt-6-astra xhigh, gpt-6.1-sol xhigh or sonnet xhigh
arena cross-judge pool: fable high or gpt-6-astra high, opus high or gpt-6.1-sol high
swarm workers: sonnet medium or gpt-6.1-sol medium
architect runners: opus xhigh or gpt-6-astra xhigh, gpt-6.1-sol xhigh or fable high
interrogate reviewers: opus xhigh or gpt-6-astra xhigh, gpt-6.1-sol xhigh or sonnet xhigh, fable high or gpt-6.1-sol xhigh
```

### 6. Confirm

Tell the user the file was written and that each skill reads it at its next role selection. Re-running this skill updates it. Name the alternatives step 4 left unverified; re-running setup on the other host confirms them.

### 7. Check verification readiness

For a mobile project, require a project `verify-<app>` skill before [mobile proof](../hugues-mode/playbooks/mobile-proof.md). If absent, offer once to generate it, even when a harness or device tools already exist. Reuse the existing harness in the generated recipe; XcodeBuildMCP or jev-ios-bridge availability alone does not supply that recipe. If generation is declined, finish model setup and explicitly hold dependent mobile proof until the recipe is available. For an existing recipe, preserve native invocation controls: unavailable, disabled, denied or unknown invocation holds dependent proof; do not replace it to evade that hold.

For a non-mobile project, an existing harness remains sufficient. Offer generation only when neither a project verification skill nor a harness exists; declining leaves model setup complete.

On acceptance, read `create-verification-skill`'s SKILL.md in full as the bundled reference and follow it, resolved from its own file or the plugin root, never the consumer workspace. Report a generated but unproved recipe as a draft with its blocker. Before later mobile proof, invoke the project recipe through the host's native mechanism; writing the file does not establish discovery or permission.

For a manual handoff, show `/hugues-stack:create-verification-skill` in Claude Code or `$create-verification-skill` in Codex, using the active host's discovered entry. End by reporting model setup and verification readiness separately, including any held proof.
