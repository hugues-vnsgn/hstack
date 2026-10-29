---
name: setup-hstack
description: Configure hStack's model and reasoning budget per role. Use when setting up hStack or changing which models it uses.
---

## Host invocation contract

Before tools, read [host contract](../../adapters/host.md)
and [mobile applicability](../../adapters/mobile.md#applicability) in full, then apply.
The host contract governs how this skill reaches any sibling dependency.

# Setup pstack

Write `.hstack/models.md` at the project root: the model-role file every pstack skill reads before it picks a worker's model.

## Role values

A role value is one or more alternatives joined by ` or `, such as `claude-opus-5-5 high or gpt-6-astra high`. Each alternative is a model and an effort.

- The model is `inherit-parent` or a real slug: a full Claude model ID such as `claude-opus-5-5` or `claude-sonnet-5-5`, or a Codex model such as `gpt-6.1-sol`. Full IDs pin the version an alias can drift from. When Claude Code's Agent tool accepts only aliases for `model`, pass the ID's alias: `claude-haiku-5-5` is `haiku`, `claude-sonnet-5-5` is `sonnet`, `claude-opus-5-5` is `opus`, and `claude-fable-5-1` is `fable`. `inherit-parent` leaves `model` unset, so the worker runs on the parent chat model. It is valid on every host.
- The effort is the last token, on the ladder `max` > `xhigh` > `high` > `medium` > `low`. It sets the agent tool's effort.
- A host runs the first alternative its agent tool accepts, so one file serves both hosts: a single-model role lists its Claude model first and its Codex model after it. With no accepted alternative, the role runs on `inherit-parent` at the first alternative's effort.
- A panel role (arena runners, architect runners, interrogate reviewers) holds a comma-separated list, and one subagent runs per entry, `inherit-parent` entries included, so the list length sets the count. Give each seat a model for both hosts and alternate which comes first, to use distinct available models where possible: `claude-opus-5-5 xhigh or gpt-6-astra xhigh, gpt-6.1-sol xhigh or claude-sonnet-5-5 xhigh` runs Opus against Sonnet in Claude Code and GPT-6-Astra against GPT-6.1-Sol in Codex. Distinct models give model diversity; a repeated model gives process independence.
- `arena cross-judge pool` is also a list, but Arena selects one value from it whose model differs from the parent's when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

## Model tiers

Step 5 gives each role a tier. When a host's model list changes, keep the tier and map it to that host's current model. Effort is the tier's default, the value a role mapped to that tier starts from.

| Tier | Claude Code | Codex | Effort | Roles |
|---|---|---|---|---|
| Fast | `claude-haiku-5-5` | `gpt-6-luna` | `xhigh` | The how explorer |
| Workhorse | `claude-sonnet-5-5` | `gpt-6.1-sol` | `high` | Code delegates, investigators, reflect tooling, swarm workers |
| Judgment | `claude-opus-5-5` | `gpt-6-astra` | `high` | Judgment and prose, hardest tasks, explainer, synthesizers, reflect reviewers, design and review seats, the cross-judge |

A role's effort can move off its tier default because effort follows the work: `medium` for parallel reading, lanes and hillclimb iterations, `high` for scoped implementation and judgment, `xhigh` for fixes, design and adversarial review. Every model in the table accepts `low` through `max`. Never write Codex's `ultra`, which delegates on its own.

## Steps

### 1. Detect available models

Read the `model` and effort values your host's native agent tool accepts from its own schema in this session. In Claude Code that is the Agent tool's `model` enum and its `effort` enum. A full Claude ID counts as detected when the enum lists it, or lists its alias and that alias resolves to the ID. On the Anthropic API each alias in the tier table resolves to its ID. A set `ANTHROPIC_DEFAULT_<FAMILY>_MODEL` must name the same ID, and on Bedrock, Vertex or Foundry the aliases name older models, so the role needs a choice. When the schema offers no model choice, the detected set is empty and every role stays on `inherit-parent`. Never write a real slug you have not confirmed is available, except the other host's alternatives, which step 4 lists as unverified.

### 2. Load current state

The starting role values are the file shape shown in step 5 below. If `.hstack/models.md` already exists, read it and treat its `# budget` line and its role values as the current choices. If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, read the legacy file and tell the user to move it. Treat its values as the current choices. Otherwise start from those values. A line whose role is not in step 5, such as `how critics`, is from a retired role. Drop it.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Prefer AskQuestion over free text. Offer these four options with these exact labels, and name the current budget when the file records one.

- `unlimited — keep max`
- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) Apply it.** Build the working table from the step 5 values, and on a re-run keep the models or list of any role whose value differs from its step 5 value. `unlimited` leaves every effort as in that table. `large`, `medium`, and `small` set the effort of every alternative, panel and `inherit-parent` entries included, to `xhigh`, `high`, or `medium`. If the agent tool does not accept that effort for that model, use its highest accepted effort below the target, else mark the role as needing a choice. So `small` turns `claude-opus-5-5 xhigh or gpt-6-astra xhigh` into `claude-opus-5-5 medium or gpt-6-astra medium`.

**(c) Show the roles and confirm.** Show every role with its value, marking any current-host slug not in the detected set as needing a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models plus `inherit-parent` as the options. Prefer AskQuestion over free text.

### 4. Validate

Every real slug written for the current host must be in the detected set. The other host's alternatives (Codex models when setup runs in Claude Code, Claude model IDs when it runs in Codex) cannot be confirmed here: keep them and list them as unverified. `inherit-parent` always passes. If a chosen real slug is not available, stop and ask again.

In Cursor, read [Cursor model roles](references/cursor-models.md) first and follow it: on the free plan every role stays on `inherit-parent`, and on a paid plan the detected Cursor id comes first in each role's alternatives.

### 5. Write the file

Write `.hstack/models.md` with a `# budget` line naming the chosen label and its target effort, and one line per role, using the role labels in [workers and models](../../adapters/host-workers.md#model-defaults-and-role-labels). Overwrite the whole file so re-runs stay idempotent. Setup writes only `.hstack/`; it never writes or deletes `.huguesstack/`. Shape:

```
# hStack model roles. One line per role. Delete a line to fall back to the skill default (`inherit-parent`).
# Value: alternatives joined by ` or `, each `<model> <effort>`. Claude models are full IDs; Claude Code passes the alias when its agent tool accepts only aliases. A host runs the first one its agent tool accepts. Panel seats alternate which host's model comes first. `inherit-parent` leaves the agent tool's `model` unset. Each comma-separated panel entry runs one subagent.
# budget: unlimited (max)
feature, refactoring: claude-sonnet-5-5 high or gpt-6.1-sol high
bug-fix: claude-sonnet-5-5 high or gpt-6.1-sol xhigh
perf-issue: claude-sonnet-5-5 high or gpt-6.1-sol xhigh
hillclimb: claude-sonnet-5-5 high or gpt-6.1-sol high
judgment and prose: claude-opus-5-5 high or gpt-6-astra high
hardest tasks: claude-opus-5-5 xhigh or gpt-6-astra high
how explorer: claude-haiku-5-5 xhigh or gpt-6-luna xhigh
how explainer: claude-opus-5-5 high or gpt-6-astra high
why investigators: claude-sonnet-5-5 high or gpt-6.1-sol high
why synthesizer: claude-opus-5-5 xhigh or gpt-6-astra high
reflect tooling: claude-sonnet-5-5 high or gpt-6.1-sol high
reflect judgment, divergent, synthesizer: claude-opus-5-5 xhigh or gpt-6-astra high
arena runners: claude-opus-5-5 xhigh or gpt-6-astra high, gpt-6.1-sol xhigh or claude-sonnet-5-5 high
arena cross-judge pool: claude-opus-5-5 xhigh or gpt-6.1-sol xhigh
swarm workers: claude-sonnet-5-5 high or gpt-6.1-sol high
architect runners: claude-opus-5-5 xhigh or gpt-6-astra high, gpt-6.1-sol xhigh
interrogate reviewers: claude-opus-5-5 xhigh or gpt-6-astra high, gpt-6.1-sol xhigh
```

### 6. Confirm

Tell the user the file was written and that each skill reads it at its next role selection. Re-running this skill updates it. Name the alternatives step 4 left unverified; re-running setup on the other host confirms them.

### 7. Check verification readiness

For a mobile project, require a project `verify-<app>` skill before [mobile proof](../hugues-mode/playbooks/mobile-proof.md). If absent, offer once to generate it, even when a harness or device tools already exist. Reuse the existing harness in the generated recipe; XcodeBuildMCP or jev-ios-bridge availability alone does not supply that recipe. If generation is declined, finish model setup and explicitly hold dependent mobile proof until the recipe is available. For an existing recipe, preserve native invocation controls: unavailable, disabled, denied or unknown invocation holds dependent proof; do not replace it to evade that hold.

For a non-mobile project, an existing harness remains sufficient. Offer generation only when neither a project verification skill nor a harness exists; declining leaves model setup complete.

On acceptance, read `create-verification-skill`'s SKILL.md in full as the bundled reference and follow it, resolved from its own file or the plugin root, never the consumer workspace. Report a generated but unproved recipe as a draft with its blocker. Before later mobile proof, invoke the project recipe through the host's native mechanism; writing the file does not establish discovery or permission.

For a manual handoff, show `/hstack:create-verification-skill` in Claude Code or `$create-verification-skill` in Codex, using the active host's discovered entry. End by reporting model setup and verification readiness separately, including any held proof.

### 8. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /create-formal-verification-skill." On yes, read `create-formal-verification-skill`'s SKILL.md in full as the bundled reference and follow it, resolved from its own file or the plugin root, never the consumer workspace. For a manual handoff, show `/hstack:create-formal-verification-skill` in Claude Code or `$create-formal-verification-skill` in Codex. On no, move on without pushing.
