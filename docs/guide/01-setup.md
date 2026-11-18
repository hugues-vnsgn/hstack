# Set up hStack

In this page you install the plugin, pick which models hStack uses, and run your first task. Setup is one command plus a short conversation.

## Install the plugin

Follow the [hStack installation instructions](../../README.md) for Claude Code or Codex, then return here to configure the consumer project.

## Pick your models

Run the active host's command:

```text
# Claude Code
/hstack:setup-hstack
# Codex
$setup-hstack
```

[`setup-hstack`](../../plugin/skills/setup-hstack/SKILL.md) detects the models you have access to, asks for a reasoning budget, shows you each role (code delegates, judgment, the review panels), and asks what you want. Answer the questions. It writes `.hstack/models.md` in your project, a small file every hStack skill reads before it picks a subagent's model.

The defaults are the same as the `large` budget. Code, prose and judgment run on Opus 5.5 at `xhigh` reasoning. Trivial edits, swarm workers, verification and the review panels run at `high`. No role runs above `xhigh`. A panel seats Fable 5.2 and Opus 5.5 at `high` beside a non-Claude seat from the Codex models. Outside a panel, Fable 5.2 runs only when you name it for a task or after two Opus 5.5 runs of the same brief fail their check. `medium` lowers each role one level and `small` lowers it two, and both spend fewer tokens.

You only override what you care about. A role with no line in the file keeps the skill's default. To restore a default, delete that role's line. A rerun of setup keeps any role whose model differs from the default. When a default changes, a file written before the change still pins the old default until you run setup again. That run replaces the old defaults it recognizes, tells you which, and keeps your other choices. To drop a pin it does not recognize, delete that role's line or the file first. If your file still says `budget: unlimited`, setup reads it as `large`, because no role runs above `xhigh`. It drops a `hardest tasks` line without asking, because that role is retired, and it says so once in its output.

Setup starts each role on a Claude model with a Codex model after it, such as `claude-opus-5-5 xhigh or gpt-6-astra xhigh`. Claude models are written as full IDs so the version stays pinned; when Claude Code's Agent tool accepts only aliases, the ID's alias (`opus`) is passed. Each host runs the first model its agent tool accepts, so one file serves Claude Code and Codex, and the budget question sets the efforts: `large`, `medium` and `small` move each role's default effort down none, one and two levels. Panel seats alternate which host's model comes first. A seat that names only a Codex model runs on the parent chat model in Claude Code, so there the panel gives independent processes, not additional model diversity. The same holds for any repeated model. Setup checks current-host availability before writing the roles. A role set to `inherit-parent` omits the subagent `model` field, so the subagent inherits your parent chat model. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Prepare verification

Setup checks whether the project can drive the real app for proof, through a project `verify-*` skill or an existing harness. If it has neither, setup offers once to generate a verification skill. Declining leaves model setup complete.

For a mobile project, setup makes the offer even when XcodeBuildMCP, jev-ios-bridge or an existing harness can drive the app, because the [mobile-proof playbook](../../plugin/skills/hugues-mode/playbooks/mobile-proof.md) needs a project `verify-<app>` recipe. The generator uses the existing tools. Declining completes model setup but leaves dependent mobile proof blocked. An unavailable or denied existing recipe also holds proof.

Accepting generates a project-local recipe under the consumer's `.claude/skills/` or `.agents/skills/` convention. The generator proves one feature before handing it over; unexecuted output remains a draft. You can start it manually with `/hstack:create-verification-skill` in Claude Code or `$create-verification-skill` in Codex, using the host's discovered entry. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers the workflow.

If you're new to hStack, accept the offer. An agent that can check its own work keeps going until the check passes. An agent that can't hands every result back to you to check by hand. Of everything in this guide, the verification skill pays off the most.

Then setup offers once to generate a formal verification skill with [`/create-formal-verification-skill`](../../plugin/skills/create-formal-verification-skill/SKILL.md), unless the project already has one. Tests check the cases someone thought to write. A formal verification skill checks one key property of your code, such as "a job never runs twice at once", in every case within a stated scope. Say yes when your code has concurrency, retries, a state machine, or a parser, where a bug is costly and tests rarely reach the case that breaks. Otherwise say no, and run it later if that changes. [Verify and ship](./06-verify-and-ship.md#prove-a-property-with-a-formal-verification-skill) covers it.

Each skill reads `.hstack/models.md` at its next role selection, so the roles apply from the next subagent spawn.

## Keep the cost in check

hStack spends extra tokens on subagents and review panels. That's the price of the rigor. To spend fewer:

- Rerun setup and pick a smaller reasoning budget or cheaper models. A strong model in the main chat with cheaper, faster models in the code roles is a good split.
- Set a role to `inherit-parent` so it runs on the chat's own model.
- Shorten a panel list. Each entry runs one subagent.
- Save `/hugues-mode` for work that needs rigor. A small, obvious edit doesn't.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
# Claude Code
/hstack:hugues-mode add a --json flag to this command. text output stays byte-identical. verify both.
# Codex
$hugues-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt.

From here you can type normal follow-ups. `hugues-mode` is sticky. It stays on for the conversation until you opt out by saying so.

Next: [Route work through `/hugues-mode`](./02-poteto-mode.md).
