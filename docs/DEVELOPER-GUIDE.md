# Use hStack 0.5.1

This guide is for version 0.5.1. It adds bundled Swift and Kotlin guidance,
mobile review and native forensics, and bounded native build/test helpers.
The hStack rename shipped in 0.4.0. Your app stays in its own repository. Skills are instruction files for
specific jobs. Playbooks order the steps of a larger task. Start with `hugues-mode` and describe the result you want.
It retains the generic workflows and applicable Swift/iOS, Kotlin/Android,
KMP and CMP proof rules.

## Before you start

Use an already installed and signed-in Claude Code or Codex. Read your app's own
instructions and preserve existing work. A source preview requires no simulator.
Executing an app requires its actual build/test tooling and your authorization.
The Python planning/audit helper requires Python 3.9+ and Git; plan validation
also requires Node. Advanced helpers may require Bun and dependencies. This guide
performs no installation or authentication setup.

## Install in Claude Code

Once its tag exists, version 0.5.1 can load for one session from a `v0.5.1` checkout.
Keep an active task on its recorded older copy until you reconcile its binding.
The 0.4.0 to 0.5.0 update was observed on both hosts. Updating to 0.5.1 remains
unobserved. Restart the Claude Code process after updating. A process started
before an update can keep loading its old cache. Follow the
[upgrade instructions](RELEASE-0.5.1.md#upgrade) for persistent installs.
Start from your app directory:

```sh
claude --plugin-dir "/absolute/path/to/hstack/plugin"
```

Check native discovery before invoking `/hstack:hugues-mode`. A package
manifest check is not evidence that invocation succeeded. Do not modify global
settings to force discovery or bypass an owner-disabled skill.

For an earlier release, use its release notes ([0.2.0](RELEASE-0.2.0.md),
[0.3.0](RELEASE-0.3.0.md)) and the instructions at that tag. Their historical
instructions use the earlier names and do not apply to this version. The
[0.5.1 release notes](RELEASE-0.5.1.md) describe the current upgrade and its
limits. The [0.4.0 notes](RELEASE-0.4.0.md) retain the historical rename and
migration from 0.3.0.

## Use Codex

Codex supports explicit skill invocation and project-native discovery. This
version supplies canonical skills plus `agents/openai.yaml` invocation metadata.
The 0.5.0 pretest used an installed Codex copy on CLI 0.163.0. The later
0.4.0 to 0.5.0 update was observed on both hosts. Updating to 0.5.1 remains
unobserved.
Use your host's supported native discovery route, and check that `hugues-mode`
is available before invoking `$hugues-mode`. Keep the complete resource layout.

If discovery or invocation is unavailable, disabled, denied or unknown, stop the
dependent workflow. Do not paste the absolute SKILL.md path as a loading fallback,
copy a disabled body under another name, or change owner settings to evade it.
See the [official skill documentation](https://learn.chatgpt.com/docs/build-skills)
for host-specific discovery and invocation controls; this guide does not invent
a plugin loader or claim a tested installation method.

## Your first task: fix a small search bug

First invoke the mode natively, then give a bounded preview request:

```text
Preview only: inspect this project's instructions and explain how search
submission works. Name the relevant files, selected playbook and unresolved
questions. Do not edit or run the app.
```

Review the explanation before authorizing the change:

```text
Fix the search field clearing before submission succeeds. Use this task's
worktree. You may edit the relevant source and run the repository's existing
local tests. Preserve unrelated work. Report the reproduction, changed behavior,
checks and any proof you could not run. Do not push or publish.
```

The workflow retains its evidence and worker requirements. When another bundled
skill is needed, the mode reads that user-only skill's file itself with the
host's own file-read tool; it uses supported native invocation only for
`hugues-mode`, `setup-hstack` and your own skills. A separate command is
needed only if the host requires explicit user invocation. A disabled or denied
native-only dependency holds its phase; the agent must not silently replace it
with a file read. These handoffs are conditional, not a proven limitation in
every session.

Inspect the actual diff and test evidence. A compilation result does not establish
screen behavior; shared changes may need both affected targets. Missing device,
tool, model or execution authority stays visible as a gap.

## Choose other work

Ask for investigation, design, review, a plan or a specific implementation result.
Give the consumer path/revision, scope and expected observable outcome. Mode
routing preserves intent before mobile domain. Specific skills remain directly
available through their native names. Generic review retains its own model panel.

## Pause and resume

Use the pause/pickup workflow to record branch, head, completed work, evidence,
remaining gates and actual worker state. In a fresh session, invoke the needed
native-only skills again and read the needed bundled user-only skills again. A
saved path or parent worker's claim does not establish current invocation
eligibility. Do not scan unrelated chat histories.

## Updating

Keep the old install while an active task is bound to it. Public skill names and
relative entry paths are retained; a changed installation root may still affect
owner settings that use absolute paths. Reconcile these explicitly through the
host's supported controls. The real controls are the plugin as a whole
(install, enable, disable) and any native denial the host applies to
`hugues-mode` or `setup-hstack`'s invocation; never silently re-enable
either after the owner disabled it. A bundled user-only skill has no separate
per-skill disablement to preserve across an update, since the agent's own file
read ignores any such setting.

Old 0.2.0 installed-payload bindings are intentionally rejected. Review the changed
workflow and plan, then create a new binding as described in
[host tools](../plugin/adapters/host-tools.md). Ordinary resource rereads remain
binding-guarded; no skill body is a helper read. `hugues-mode`, `setup-hstack`
and consumer or external skills require native invocation, a bundled user-only
skill's SKILL.md is read with the host's own file-read tool, and a plan names the
skill to apply instead of a path. The plan translator holds on every raw-skill
read so the author can correct the plan explicitly.

## Removing it

A session-only Claude load ends with that session. Persistent installs
must be removed through the host mechanism that installed them, under your scope.
Keep checkouts or evidence still referenced by unfinished tasks; this guide does
not delete worktrees, active/pinned chats or user data.

## Troubleshooting

Missing native entry: check the host's supported discovery surface; stop rather
than using a raw-body fallback. Binding drift: reconcile the installation and
program, never regenerate hashes to conceal an unexpected change. Missing activity
or PR metadata: the read-only cleanup report holds candidates. No report grants
deletion authority, and active/pinned-chat verification is a separate gate.

## What has been verified

Current source, contract, integrity and helper checks are described in
[test accounting](TEST-COVERAGE.md) and [migration notes](NATIVE-CONSOLIDATION.md).
They use disposable local consumers and synthetic activity. The earlier bounded
host trials were blocked before complete planning/invocation. Three bounded
receipts cover this layout: the [skill-list host validation](skill-list-host-validation.md),
the [router eval](hugues-mode-router-eval.md) and the [router interactive
check](router-interactive-check.md), whose one Claude Code session fired the
router and spawned arena candidates but stopped before any finished.
The [0.5.0 validation](RELEASE-0.5.0.md#validation) records later bounded
bug-fix runs on Codex and Claude Code, plus helper and Chrome checks. Both final
workflows wrote their todos late. Claude used headless bypassPermissions with
hooks off. Interactive normal-permission completion, native runtime parity,
persisted-transcript coverage, complete mobile journeys and live forge/cloud/loop
workflows remain unverified. The [0.5.1 validation](RELEASE-0.5.1.md#validation)
adds native helper observations. The host/domain mobile workflow matrix remains
unobserved on both hosts.
