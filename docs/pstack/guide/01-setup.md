# Set up pstack

In this page you install the plugin, pick which models pstack uses, and run your first task. Setup is one command plus a short conversation.

## Install the plugin

Follow the [hStack installation instructions](../../../README.md) for Claude Code or Codex, then return here to configure the consumer project.

## Pick your models

Run the active host's command:

```text
# Claude Code
/hstack:setup-hstack
# Codex
$setup-hstack
```

[`setup-hstack`](../../../plugin/skills/setup-hstack/SKILL.md) detects the models you have access to, asks for a reasoning budget, shows you each role (code delegates, judgment, the review panels), and asks what you want. Answer the questions. It writes `.hstack/models.md` in your project, a small file every pstack skill reads before it picks a subagent's model.

You only override what you care about. A role with no line in the file keeps the skill's default. To restore a default, delete that role's line. A rerun of setup keeps any role whose model differs from the default. When a default changes, a file written before the change still pins the old default, so delete those role lines, or delete the file, then run setup again.

Setup starts each role on a Claude model with a Codex model after it, such as `sonnet high or gpt-6.1-sol high`. Each host runs the first model its agent tool accepts, so one file serves Claude Code and Codex, and the budget question sets the efforts: `unlimited` keeps each role at the effort setup lists, up to `max`, while `large`, `medium` and `small` set every role to `xhigh`, `high` or `medium`, and a lower effort spends fewer tokens. Panel seats alternate which host's model comes first. The default interrogate panel has three seats; Codex uses GPT-6-Astra and two GPT-6.1-Sol seats. Repeated models provide independent processes, not additional model diversity. Setup checks current-host availability before writing the roles. A role with no line runs on `inherit-parent`: pstack omits the subagent `model` field, so the subagent inherits your parent chat model. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Prepare verification

For mobile projects, setup looks for a project `verify-<app>` skill, even when XcodeBuildMCP, jev-ios-bridge or an existing harness can drive the app. The [mobile-proof playbook](../../../plugin/skills/hugues-mode/playbooks/mobile-proof.md) needs that recipe. If it is absent, setup offers once to generate one using the existing tools. Declining completes model setup but leaves dependent mobile proof blocked. An unavailable or denied existing recipe also holds proof.

For non-mobile projects, an existing harness remains sufficient. Setup offers generation when neither a verification skill nor a harness exists.

Accepting generates a project-local recipe under the consumer's `.claude/skills/` or `.agents/skills/` convention. The generator proves one feature before handing it over; unexecuted output remains a draft. You can start it manually with `/hstack:create-verification-skill` in Claude Code or `$create-verification-skill` in Codex, using the host's discovered entry. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers the workflow.

If you're new to pstack, accept the offer. An agent that can check its own work keeps going until the check passes. An agent that can't hands every result back to you to check by hand. Of everything in this guide, the verification skill pays off the most.

Each skill reads `.hstack/models.md` at its next role selection, so the roles apply from the next subagent spawn.

## Prepare an autopilot program

Both autopilot workflows require [read-only payload protection](../../../plugin/adapters/payload-protection.md)
before write-capable work. Review the generated native host configuration, retain
your existing settings and verify the boundary for the coordinator and workers.
Uncovered writers or unsupported host protection hold the program. Plugin
maintenance belongs to a separate owner-authorized task.

## Keep the cost in check

pstack spends extra tokens on subagents and review panels. That's the price of the rigor. To spend fewer:

- Rerun setup and pick a smaller reasoning budget or cheaper models. A strong model in the main chat with cheaper, faster models in the code roles is a good split.
- Set a role to `inherit-parent` so it runs on the chat's own model.
- Shorten a panel list. Each entry runs one subagent.
- Save `/hugues-mode` for work that needs rigor. A small, obvious edit doesn't.

## Prepare an unattended Claude stack

If you plan to use `autopilot-stack` in Claude Code auto mode, ask
`/setup-hstack` to prepare its stack permissions. It shows a rule for the
repository and child branches you approve, then checks Claude's effective
configuration. The [permission recipe](../../../plugin/adapters/claude-stack-permissions.md)
keeps pstack's rebase workflow and its operator landing gates. Approval applies
throughout that recorded scope; adding branches needs a new scope ruling.
Model-only setup and other hosts keep their existing behavior.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
# Claude Code
/hstack:hugues-mode add a --json flag to this command. text output stays byte-identical. verify both.
# Codex
$hugues-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `hugues-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. `hugues-mode` is sticky. It stays on for the conversation until you opt out by saying so.

Next: [Route work through `/hugues-mode`](./02-poteto-mode.md).
