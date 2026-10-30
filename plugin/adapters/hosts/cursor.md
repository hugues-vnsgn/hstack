# Cursor

You are running in the Cursor IDE. Read this page before the first tool call, then follow the `Cursor` column in [host.md](../host.md); the other columns are those hosts' instructions.

| Row | Mechanics |
|---|---|
| Detect | You are running in the Cursor IDE. |
| Sessions and worktrees | One source only: if you use hStack in Claude Code, install nothing in Cursor, since Cursor loads hStack from Claude Code's install; otherwise hold a copy of the plugin tree at `~/.cursor/plugins/local/hstack`. Cursor loads the Claude plugin cache as well as `~/.cursor/plugins/local/`, and de-duplicates within one plugin rather than across plugins, so two sources register every shared skill twice. |
| Start | Follow the `Cursor` column; the other columns are those hosts' instructions. |
| Send | unobserved |
| Read | Cursor transcripts live at `~/.cursor/projects/<slug>/agent-transcripts/`. A record carries no `cwd` and no record-level timestamp, and it may carry no tool results. |
| Wait | A Cursor plugin agent runs in the foreground: dispatch it and wait in the same turn, and say it ran in the foreground. |
| Close | unobserved |
| Load a PR head | unobserved |
| Allowed tools | The `Cursor` column of the [host.md](../host.md) tables. `readonly: true` and `readonly: false` are native as written: a read-only worker keeps its file reads and makes no edit. Per Cursor's loader, not observed in the IDE. Cursor registers the plugin's own agents, so `hugues-agent` is a subagent there: observed in the IDE on 2026-10-30, where a `Task` call with `subagent_type: "hugues-agent"` ran one helper task in the foreground and reported back. `run_in_background: true` has no native field there. The agent tool exposes its own model ids and no effort parameter: observed in the IDE on 2026-10-30, where the schema listed one real model id plus `inherit`, and where a role's effort token was recorded but the worker ran at the host's effort. Detect the ids from the agent tool's own schema in the session, and never write a Cursor model id the agent tool did not list. |
| Skip line | Skipped in Cursor: <step>. <reason>. A free Cursor feature is native in Cursor. A feature that needs a paid Cursor plan keeps the skip line, and it is skipped on every host, including Cursor. The paid rows are Cursor Automations, Bugbot, and Cursor cloud agents with the Cursor SDK and T3 Code's Cursor provider; a step that needs the cloud agent itself is Cursor-only. A local worktree worker substitutes only where the core permits local execution. |

### The Cursor-only features, one action each

The free rows are native in Cursor, so they run with no skip line. A built-in
PR tool uses the step's forge command, such as `gh pr create`, with no line. A
"control skill" or "matching control skill" and its `cursor-team-kit`
attributions use the bundled `control-cli` for a CLI or TUI and `control-ui`
for a browser, Electron or web UI; on iOS or Android, the repo's installed
simulator-driving skill, such as `test-ios` or `test-android`, through the
native mechanism, else XCTest or UiAutomator through the native helper, and a
missing driver stays an execution gap. Cursor's `/loop` is the native `/loop`
in the current local session, never a cloud schedule for work that needs local
devices, and between-turn scheduling stays an unsatisfied gap per #34 item 6.

The paid rows skip with the line. Cursor Automations covers routines,
`update_state` routine calls, `api2.cursor.sh/automations` webhooks, routine
wakes and `SendToUser` secret requests. Bugbot covers a Bugbot review. Cursor
cloud agents covers `environment: "cloud"`, the Cursor SDK and T3 Code's
Cursor provider, where a step that needs the cloud agent itself is Cursor-only
and a local worktree worker substitutes only where the core permits local
execution. Per Cursor's loader; not observed in the IDE.

## Where a skill is edited in Cursor

Never edit a skill under `plugins/cache/` (`~/.claude/plugins/cache/`,
`~/.codex/plugins/cache/` or `~/.cursor/plugins/local/`). Before approval, show
its destination: `.claude/skills/<skill>/` or `~/.claude/skills/<skill>/` in
Claude Code, `.agents/skills/<skill>/` or `~/.agents/skills/<skill>/` in Codex,
and `.cursor/skills/<skill>/` or `~/.cursor/skills/<skill>/` in Cursor. After
approval, copy the skill folder there and edit the copy. Never open a PR or
push.

## A commit in Cursor

Observed in the IDE on 2026-10-30: Cursor's shell wrapper adds a
`Co-authored-by: Cursor <cursoragent@cursor.com>` trailer to every
`git commit`, and `git commit --amend` adds it again. No git hook, local
config or alias produces it.

Never bypass hooks to remove the trailer. If a project forbids the trailer,
say so and leave the commit to the user.

## The one-source evidence

Both halves of the one-source observation come from one lab session on 2026-10-30 with both sources present, observed in Cursor 3.27.22 with a third-party auth extension: that session loaded `hstack` from the local copy (`loadUserLocalPlugin`) and from `~/.claude/plugins/cache/hstack/hstack/0.5.6` (`loadClaudePlugin hstack@hstack`), and ran the `host-detect.sh` hook once per copy. Route A, loading from Claude Code's install, is expected, not proven: it is checked at the end, on the released plugin, with hStack on in Claude Code and no local copy. Stock Cursor is unobserved, and so is the free plan without the third-party auth extension.
