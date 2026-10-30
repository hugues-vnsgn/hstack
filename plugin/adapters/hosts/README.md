# Hosts and ADEs

[host-workers.md](../host-workers.md) sends you here when `$ORCA_TERMINAL_HANDLE`, `$ORCA_PANE_KEY` or `$ORCA_TAB_ID` is set, `t3-code` tools are listed, or the agent is omp. Read this once. Run each list's detection test, read the page of the first match, and go on under host.md when none matches.

Each list line reads `- [name](name.md): detection test`.

Unobserved: omp matches at dispatch, not its first tool call, so an omp agent that never dispatches reads no page. Codex's `shell_environment_policy` may strip `ORCA_TERMINAL_HANDLE` in Orca. Every process an Orca pane starts inherits it. A Claude Code hook also sends you here.

## Shared ADE rule

A page maps terminal and worktree mechanics only: which session and worktree a worker runs in, so the coordinator can send, read and wait on it. hStack's playbooks keep dispatch, completion, verification and every record. A page never creates or reads the ADE's own runs, tasks, dispatches, inboxes or settlement receipts. New work gets a fresh worker.

## Page shape

Each agent or ADE gets one page, `<name>.md`, with one table `| Row | Mechanics |` and these rows in order: Detect, Sessions and worktrees, Start, Send, Read, Wait, Close, Load a PR head, Allowed tools, Skip line. The Skip line row holds `Skipped in <name>: <step>. <reason>.`. Write `unobserved` for what hStack has not seen. A page adds no gate or authority and edits no file the upstream ledger maps.

## Agents

- [Cursor](cursor.md): you are running in the Cursor IDE.

## ADEs

- [Orca](orca.md): `$ORCA_TERMINAL_HANDLE`, `$ORCA_PANE_KEY` or `$ORCA_TAB_ID` is set.
