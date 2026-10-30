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
| Allowed tools | The `Cursor` column of the [host.md](../host.md) tables. `readonly: true` and `readonly: false` are native as written: a read-only worker keeps its file reads and makes no edit. Per Cursor's loader, not observed in the IDE. Cursor registers the plugin's own agents, so `hugues-agent` is a subagent there. Per Cursor's loader, not observed in the IDE. `run_in_background: true` has no native field there. On Cursor's free plan the IDE exposes no per-model choice to the agent tool, so the detected model set is empty and every role stays on `inherit-parent`. Per Cursor's loader, not observed in the IDE: P1 found `model` stripped for plugin agents. On a paid plan the IDE exposes model ids the agent tool accepts; detect them from the agent tool's own schema in the session. Never write a Cursor model id the agent tool did not list. |
| Skip line | Skipped in Cursor: <step>. <reason>. A free Cursor feature is native in Cursor. A feature that needs a paid Cursor plan keeps the skip line, and it is skipped on every host, including Cursor. The paid rows are Cursor Automations, Bugbot, and Cursor cloud agents with the Cursor SDK and T3 Code's Cursor provider; a step that needs the cloud agent itself is Cursor-only. A local worktree worker substitutes only where the core permits local execution. |

## Where a skill is edited in Cursor

Never edit a skill under `plugins/cache/` (`~/.claude/plugins/cache/`,
`~/.codex/plugins/cache/` or `~/.cursor/plugins/local/`). Before approval, show
its destination: `.claude/skills/<skill>/` or `~/.claude/skills/<skill>/` in
Claude Code, `.agents/skills/<skill>/` or `~/.agents/skills/<skill>/` in Codex,
and `.cursor/skills/<skill>/` or `~/.cursor/skills/<skill>/` in Cursor. After
approval, copy the skill folder there and edit the copy. Never open a PR or
push.
## One-source evidence

Both halves of the one-source observation come from one lab session on 2026-10-30 with both sources present, observed in Cursor 3.27.22 with a third-party auth extension: that session loaded `hstack` from the local copy (`loadUserLocalPlugin`) and from `~/.claude/plugins/cache/hstack/hstack/0.5.6` (`loadClaudePlugin hstack@hstack`), and ran the `host-detect.sh` hook once per copy. Route A, loading from Claude Code's install, is expected, not proven: lane 1b has not passed yet. Stock Cursor is unobserved, and so is the free plan without the third-party auth extension.
