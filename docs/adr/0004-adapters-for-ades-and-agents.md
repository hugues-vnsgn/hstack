---
status: accepted
---

# Adapters for ADEs and for agents beyond Claude Code and Codex

An adapter for an ADE, or for an agent beyond Claude Code and Codex, is allowed if it only maps mechanics, adds no gate or authority, adds no always-read bytes beyond the door row, and edits no ledger-mapped file.

hStack follows pstack. pstack's own Claude Code adapter, `docs/harness/claude-code.md`, is a set of lookup tables from Cursor's names to the host's, plus one rule for the features the host lacks. A new host or ADE earns the same thing and nothing more. The four conditions keep it that way.

- **Only maps mechanics.** A page says how to detect the host, where its sessions and worktrees live, and how to start, send to, read, wait on and close a worker. Workflow phases, gates, panel sizes and stop rules stay in the canonical skills and [host.md](../../plugin/adapters/host.md).
- **Adds no gate or authority.** A page cannot lift a hold or grant a permission. A skip line never checks a gate.
- **Adds no always-read bytes beyond the door row.** The door began as a row in the phase table of [host.md](../../plugin/adapters/host.md), which two of three Orca sessions in P2's lane 10 skipped. It is now one sentence at the top of [host-workers.md](../../plugin/adapters/host-workers.md), which a session reads before its first dispatch, and it tells the session to run `printenv ORCA_TERMINAL_HANDLE`. So host.md, which every session reads, carries none of it. Everything else loads from [hosts/README.md](../../plugin/adapters/hosts/README.md) only when a session meets the door's test, and a page loads only when the session matches an ADE or an agent listed there. The hook below adds no always-read bytes either: the host delivers its message, not an adapter every session reads.
- **Edits no ledger-mapped file.** The upstream ledger maps every pstack file. An adapter lives in unmapped files, so a later pstack re-pin merges without touching it.

## The door is a hook, and the written check stays

Prose could not make the door fire. Across P2's rounds 2 to 4, a session that read [host-workers.md](../../plugin/adapters/host-workers.md) still skipped the test in 2 of 6 Orca runs, and the runs that skipped it never mentioned Orca at all. A session that does not run the test cannot be told to run it in the same breath.

So hStack ships its first hook: a `SessionStart` command hook in [hooks.json](../../plugin/hooks/hooks.json) that runs [host-detect.sh](../../plugin/hooks/host-detect.sh) at session start. The script tests the Orca variables and, when one is set, tells the session to read the hosts index before its first dispatch. It names the index and no page, and it grants no gate and no authority. A session that meets no test gets no output and no bytes.

Observed: in an Orca 1.4.241 pane, `ORCA_TERMINAL_HANDLE`, `ORCA_PANE_KEY` and `ORCA_TAB_ID` are all set, and the hook fires in Claude Code 2.1.311.

The written check stays, for three reasons. Codex and omp load no plugin hook, so the written check is their only path. A T3 Code thread exposes no Orca variable, and the hook cannot see the tools a session was given, so the written check covers it. And the written check names the same three variables the hook tests, so a session that meets the hook's test also meets the written one.

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
- A test reads the hook's manifest and script: one `SessionStart` command hook, the three Orca variables it tests, the index it names, no page, and no authority in its message. A plain session gets no output.
- Unobserved: an Orca, T3 Code or omp session reading the door. Static tests prove the wiring only. The index names the door's limits: omp matches at dispatch rather than its first tool call, Codex may strip `ORCA_TERMINAL_HANDLE` in Orca, and every process an Orca pane starts inherits it. The hook covers Claude Code only, and it adds a runtime hook pstack lacks.
