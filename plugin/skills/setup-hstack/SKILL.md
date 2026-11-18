---
name: setup-hstack
description: Configure hStack's model and reasoning budget per role. Use when setting up hStack or changing which models it uses.
---

## Host invocation contract

Before tools, read [host contract](../../adapters/host.md) in full, then apply.
The host contract governs how this skill reaches any sibling dependency.

# Setup hStack

Write `.hstack/models.md` at the project root: the model-role file every hStack skill reads before it picks a worker's model.

## Role values

A role value is one or more alternatives joined by ` or `, such as `claude-opus-5-5 high or gpt-6-astra high`. Each alternative is a model and an effort.

- The model is `inherit-parent` or a real slug: a full Claude model ID such as `claude-opus-5-5` or `claude-sonnet-5-5`, or a Codex model such as `gpt-6.1-sol`. Full IDs pin the version an alias can drift from. When Claude Code's Agent tool accepts only aliases for `model`, pass the ID's alias: `claude-haiku-5-5` is `haiku`, `claude-sonnet-5-5` is `sonnet`, `claude-opus-5-5` is `opus`, and `claude-fable-5-2` is `fable`. `inherit-parent` leaves `model` unset, so the worker runs on the parent chat model. It is valid on every host.
- The effort is the last token, on the ladder `xhigh` > `high` > `medium` > `low`. It sets the agent tool's effort. No role runs above `xhigh`, so setup never writes `max`.
- A host runs the first alternative its agent tool accepts, so one file serves every host: a single-model role lists the current host's model first and the other hosts' alternatives after it. With no accepted alternative, the role runs on `inherit-parent` at the first alternative's effort.
- A panel role (arena runners, interrogate reviewers) holds a comma-separated list, and one subagent runs per entry, `inherit-parent` entries included, so the list length sets the count. Give each seat a model for every host and alternate which comes first, to use distinct available models where possible: `claude-fable-5-2 high or gpt-6-astra high, gpt-6.1-sol high or claude-opus-5-5 high` runs Fable against Opus in Claude Code and GPT-6-Astra against GPT-6.1-Sol in Codex. Distinct models give model diversity; a repeated model gives process independence.
- `arena cross-judge pool` is also a list, but Arena runs one judge. It tries values from another vendor than the parent's first, then values whose model differs from the parent's, in list order, so order it by preference. An `inherit-parent` value never judges. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

## Model tiers

Step 5 gives each role a tier. When a host's model list changes, keep the tier and map it to that host's current model. Effort is the tier's default, the value a role mapped to that tier starts from.

| Tier | Claude Code | Codex | Effort | Roles |
|---|---|---|---|---|
| Primary | `claude-opus-5-5` | `gpt-6-astra` | `xhigh` | Code delegates, judgment and prose |
| Light | `claude-opus-5-5` | `gpt-6.1-sol` | `high` | Swarm workers, trivial mechanical edits, verification, the cross-judge, one seat in each panel |
| Fable seat | `claude-fable-5-2` | `gpt-6-astra` | `high` | One seat in each panel, never a single-model role |

A role's effort moves off its tier default only through the budget in step 3 and the router's match-the-model rule. Every model in the table accepts `low` through `max`, but no role runs above `xhigh`. Never write Codex's `ultra`, which delegates on its own.

A Fable seat names the Primary tier's Claude model as its next alternative, so a host whose agent tool does not accept Fable runs the seat on Opus. Fable runs outside a panel only when the user names it or two Opus runs of the same brief fail its check.

## Steps

### 1. Detect available models

Read the `model` and effort values your host's native agent tool accepts from its own schema in this session. In Claude Code that is the Agent tool's `model` enum and its `effort` enum. A full Claude ID counts as detected when the enum lists it, or lists its alias and that alias resolves to the ID. On the Anthropic API each alias in the tier table resolves to its ID. A set `ANTHROPIC_DEFAULT_<FAMILY>_MODEL` must name the same ID, and on Bedrock, Vertex or Foundry the aliases name older models, so the role needs a choice. When the schema offers no model choice, the detected set is empty and every role stays on `inherit-parent`. Never write a real slug you have not confirmed is available, except the other hosts' alternatives, which step 4 lists as unverified.

### 2. Load current state

The starting role values are the file shape shown in step 5 below. If `.hstack/models.md` already exists, read it and treat its `# budget` line and its role values as the current choices. If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, read the legacy file and tell the user to move it. Treat its values as the current choices. Otherwise start from those values. A line whose role is not in step 5 is from a retired role. Drop it without asking. The retired roles include `hardest tasks`, `how explorer`, `how explainer`, `why investigators`, `why synthesizer`, `architect runners`, `reflect tooling` and `reflect judgment, divergent, synthesizer`.

A file without the `# defaults: 3` line comes from an older setup. Before step 3, read its `# budget: unlimited` line as `large`, because no role runs above `xhigh`. Do not ask about this or about the dropped roles. Mention both changes once in step 6.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Prefer AskQuestion over free text. Offer these three options with these exact labels, and name the current budget when the file records one. With no file, say that `large` matches the skill defaults.

- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) Apply it.** Build the working table from the step 5 values, and on a re-run keep the models or list of any role whose models differ from its step 5 value. Each role has a target effort, which is its step 5 effort moved by the budget. `large` keeps it, `medium` lowers it one step, and `small` lowers it two steps, on the ladder `xhigh` > `high` > `medium` > `low`. A target at the bottom of the ladder stays there. Set the effort of every alternative in the role, panel and `inherit-parent` entries included, to the role's target. If the agent tool does not accept that effort for that model, use its highest accepted effort below the target, else mark the role as needing a choice. So `medium` turns `claude-opus-5-5 xhigh or gpt-6-astra xhigh` into `claude-opus-5-5 high or gpt-6-astra high` and `claude-opus-5-5 high or gpt-6.1-sol high` into `claude-opus-5-5 medium or gpt-6.1-sol medium`.

**(c) Show the roles and confirm.** Show every role with its value, marking any current-host slug not in the detected set as needing a choice. A role that also lists a detected current-host alternative needs no choice: drop the undetected one, say so, and the role runs the next. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models at `xhigh` or below plus `inherit-parent` as the options. Prefer AskQuestion over free text.

### 4. Validate

Every real slug written for the current host must be in the detected set and at `xhigh` or below. The other hosts' alternatives (Codex and Cursor models when setup runs in Claude Code, Claude model IDs when it runs in Codex, and so on) cannot be confirmed here: keep them and list them as unverified. `inherit-parent` always passes. If a chosen real slug is not available, stop and ask again.

In Cursor, read [Cursor model roles](references/cursor-models.md) first and follow it: detect the Cursor model ids from the agent tool's own schema in the session, and put the detected id first in each role's alternatives.

### 5. Write the file

Write `.hstack/models.md` with the `# defaults: 3` line, a `# budget` line naming the chosen label and the effort that label names, and one line per role, using the role labels in [workers and models](../../adapters/host-workers.md#model-defaults-and-role-labels). Overwrite the whole file so re-runs stay idempotent. Setup writes only `.hstack/`; it never writes or deletes `.huguesstack/`. Shape:

```
# hStack model roles. One line per role. Delete a line to fall back to the skill default.
# Value: alternatives joined by ` or `, each `<model> <effort>`. Claude models are full IDs; Claude Code passes the alias when its agent tool accepts only aliases. A host runs the first one its agent tool accepts. Panel seats alternate which host's model comes first. `inherit-parent` leaves the agent tool's `model` unset. Each comma-separated panel entry runs one subagent.
# defaults: 3
# budget: large (xhigh)
feature, refactoring: claude-opus-5-5 xhigh or gpt-6-astra xhigh
bug-fix: claude-opus-5-5 xhigh or gpt-6-astra xhigh
perf-issue: claude-opus-5-5 xhigh or gpt-6-astra xhigh
hillclimb: claude-opus-5-5 xhigh or gpt-6-astra xhigh
judgment and prose: claude-opus-5-5 xhigh or gpt-6-astra xhigh
arena runners: claude-fable-5-2 high or claude-opus-5-5 high or gpt-6-astra high, claude-opus-5-5 high or gpt-6.1-sol high, gpt-6-astra high or claude-opus-5-5 high
arena cross-judge pool: claude-opus-5-5 high or gpt-6.1-sol high, gpt-6-astra high or claude-opus-5-5 high
swarm workers: claude-opus-5-5 high or gpt-6.1-sol high
interrogate reviewers: claude-fable-5-2 high or claude-opus-5-5 high or gpt-6-astra high, claude-opus-5-5 high or gpt-6.1-sol high, gpt-6-astra high or claude-opus-5-5 high
```

### 6. Confirm

Tell the user the file was written and that each skill reads it at its next role selection. Re-running this skill updates it. If step 2 read `unlimited` as `large` or dropped a retired role, say so once. Name the alternatives step 4 left unverified; re-running setup on the other host confirms them.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof: a project `verify-*` skill or an existing harness. If it has neither, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one." On no, move on without pushing. Model setup is complete either way.

For a mobile project, [mobile proof](../hugues-mode/playbooks/mobile-proof.md) needs a project `verify-<app>` skill, so make the offer even when a harness or device tools already exist. Reuse the existing harness in the generated recipe; XcodeBuildMCP or jev-ios-bridge availability alone does not supply that recipe. If generation is declined, finish model setup and explicitly hold dependent mobile proof until the recipe is available. For an existing recipe, preserve native invocation controls: unavailable, disabled, denied or unknown invocation holds dependent proof; do not replace it to evade that hold.

On yes, read `create-verification-skill`'s SKILL.md in full as the bundled reference and follow it, resolved from its own file or the plugin root, never the consumer workspace. Report a generated but unproved recipe as a draft with its blocker. Before later mobile proof, invoke the project recipe through the host's native mechanism; writing the file does not establish discovery or permission.

For a manual handoff, show `/hstack:create-verification-skill` in Claude Code or `$create-verification-skill` in Codex, using the active host's discovered entry. End by reporting model setup and verification readiness separately, including any held proof.

### 8. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /create-formal-verification-skill." On yes, read `create-formal-verification-skill`'s SKILL.md in full as the bundled reference and follow it, resolved from its own file or the plugin root, never the consumer workspace. For a manual handoff, show `/hstack:create-formal-verification-skill` in Claude Code or `$create-formal-verification-skill` in Codex. On no, move on without pushing.
