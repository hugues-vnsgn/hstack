# Hosts and ADEs

Read this once, before the first dispatch in an ADE or the first tool call in an agent listed below. Run each list's detection test, read the page of the first match, and go on under [host.md](../host.md) when none matches.

An ADE hosts agent sessions and worktrees. An agent here is a program that runs a model, not a PR owner. Each list line reads `- [name](name.md): detection test`.

## Shared ADE rule

A page maps terminal and worktree mechanics only: which session and worktree a worker runs in, so the coordinator can send, read and wait on it. hStack's playbooks keep dispatch, completion, verification and every record. A page never creates or reads the ADE's own runs, tasks, dispatches or inboxes. New work gets a fresh worker.

## Page shape

One page per agent or ADE, `<name>.md`, holding one table `| Row | Mechanics |` whose rows come in this order: Detect, Sessions and worktrees, Start, Send, Read, Wait, Close, Load a PR head, Allowed tools, Skip line. The Skip line row holds `Skipped in <name>: <step>. <reason>.`. Write `unobserved` for what hStack has not seen. A page adds no gate or authority and edits no file the upstream ledger maps.

## Agents

## ADEs
