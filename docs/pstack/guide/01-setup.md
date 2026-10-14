# Set up pstack

In this page you install the plugin, pick which models pstack uses, and run your first task. Setup is one command plus a short conversation.

## Install the plugin

Follow the [huguesStack installation instructions](../../../README.md) for Claude Code or Codex, then return here to configure the consumer project.

## Pick your models

Run the active host's command:

```text
# Claude Code
/hugues-stack:setup-huguesstack
# Codex
$setup-huguesstack
```

[`setup-huguesstack`](../../../plugin/skills/setup-huguesstack/SKILL.md) detects the models you have access to, asks for a reasoning budget, shows you each role (code delegates, judgment, the review panels), and asks what you want. Answer the questions. It writes `.huguesstack/models.md` in your project, a small file every pstack skill reads before it picks a subagent's model.

You only override what you care about. A role with no line in the file keeps the skill's default. To restore a default, delete that role's line. A rerun of setup keeps any role whose model differs from the default.

Setup starts each role on a Claude model with a Codex model after it, such as `sonnet high or gpt-6.1-sol high`. Each host runs the first model its agent tool accepts, so one file serves Claude Code and Codex, and the budget question sets the efforts. Panel seats alternate which host's model comes first. The default interrogate panel has three seats; Codex uses GPT-6-Astra and two GPT-6.1-Sol seats. Repeated models provide independent processes, not additional model diversity. Setup checks current-host availability before writing the roles. A role with no line runs on `inherit-parent`: pstack omits the subagent `model` field, so the subagent inherits your parent chat model. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Prepare verification

For mobile projects, setup looks for a project `verify-<app>` skill, even when XcodeBuildMCP, jev-ios-bridge or an existing harness can drive the app. The [mobile-proof playbook](../../../plugin/skills/hugues-mode/playbooks/mobile-proof.md) needs that recipe. If it is absent, setup offers once to generate one using the existing tools. Declining completes model setup but leaves dependent mobile proof blocked. An unavailable or denied existing recipe also holds proof.

For non-mobile projects, an existing harness remains sufficient. Setup offers generation when neither a verification skill nor a harness exists.

Accepting generates a project-local recipe under the consumer's `.claude/skills/` or `.agents/skills/` convention. The generator proves one feature before handing it over; unexecuted output remains a draft. You can start it manually with `/hugues-stack:create-verification-skill` in Claude Code or `$create-verification-skill` in Codex, using the host's discovered entry. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers the workflow.

After setup, start a new chat. The model rule applies to new sessions.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
# Claude Code
/hugues-stack:hugues-mode add a --json flag to this command. text output stays byte-identical. verify both.
# Codex
$hugues-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `hugues-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. `hugues-mode` is sticky. It stays on for the conversation until you opt out by saying so.

Next: [Route work through `/hugues-mode`](./02-poteto-mode.md).
