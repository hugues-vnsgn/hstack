---
status: accepted
---

# Adapters for ADEs and for agents beyond Claude Code and Codex

An adapter for an ADE, or for an agent beyond Claude Code and Codex, is allowed if it only maps mechanics, adds no gate or authority, adds no always-read bytes beyond the door row, and edits no ledger-mapped file.

hStack follows pstack. pstack's own Claude Code adapter, `docs/harness/claude-code.md`, is a set of lookup tables from Cursor's names to the host's, plus one rule for the features the host lacks. A new host or ADE earns the same thing and nothing more. The four conditions keep it that way.

- **Only maps mechanics.** A page says how to detect the host, where its sessions and worktrees live, and how to start, send to, read, wait on and close a worker. Workflow phases, gates, panel sizes and stop rules stay in the canonical skills and [host.md](../../plugin/adapters/host.md).
- **Adds no gate or authority.** A page cannot lift a hold or grant a permission. A skip line never checks a gate.
- **Adds no always-read bytes beyond the door row.** [host.md](../../plugin/adapters/host.md) gets one row in its phase table, worded by timing and under 100 bytes. Everything else loads from [hosts/README.md](../../plugin/adapters/hosts/README.md) only when a session meets the door row's test, and a page loads only when the session matches an ADE or an agent listed there.
- **Edits no ledger-mapped file.** The upstream ledger maps every pstack file. An adapter lives in unmapped files, so a later pstack re-pin merges without touching it.

## Terms

An ADE (agent development environment) is an app that hosts several agent sessions and their worktrees, such as Orca or T3 Code. An agent is a program that runs a model, such as Claude Code, Codex or omp. Neither is the glossary's Layer 1 or Layer 2, and an agent here is not a PR owner. Claude Code and Codex stay in [host.md](../../plugin/adapters/host.md), which is the contract for every session.

## The shared ADE rule

The rule is stated once, in [hosts/README.md](../../plugin/adapters/hosts/README.md#shared-ade-rule), because sessions read that file. This ADR does not repeat it, so the two cannot differ.

## Orca is terminal-only

This is [#50](https://github.com/hugues-vnsgn/hstack/issues/50) after its 2026-10-19 correction. The Orca page uses `orca-cli` for terminals and worktrees, resolving a pane's `tabId:leafId` to a terminal handle. It does not use Orca's `orchestration` skill, so hStack does the coordinating and Orca only hosts the agents' terminals and worktrees.

## Consequences

- P2 ships the door and an empty index. A page lands with its own detection test and its own observed evidence. A mechanic hStack has not seen on the host is written `unobserved`.
- A session that meets no door test reads nothing under `plugin/adapters/hosts/`. A session that meets one reads the index, `hosts/README.md`, and reads a page only for a listed ADE or agent it matches. So a session outside every listed ADE and agent reads at most the index, never a page.
- A test reads each page for its rows in order and a skip line, and checks that the index lists exactly the pages that exist.
- Unobserved: an Orca, T3 Code or omp session reading the door row. Static tests prove the wiring only. The index names the door's limits: omp matches at dispatch rather than its first tool call, Codex may strip `ORCA_TERMINAL_HANDLE` in Orca, and every process an Orca pane starts inherits it.
