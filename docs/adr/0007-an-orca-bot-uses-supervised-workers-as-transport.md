---
status: accepted
---

# An Orca bot uses supervised workers as transport

Inside an Orca bot chat, hStack uses Orca's supervised workers, their `worker_done` mail and Orca items to start work, to be woken when it ends and to ask the owner a blocking question. hStack still plans the work, writes the brief, runs the independent check and gives the verdict. An Orca pane stays terminal-only, as [ADR 0004](0004-adapters-for-ades-and-agents.md) says. Using a bot is still Layer 1, and Layer 2 stays deferred.

This is an ADE adapter, the first kind in [ADR 0006](0006-follow-upstream-and-record-what-hstack-adds.md), and a fix for friction seen in a canary bot's transcripts. It has no upstream file, so its reason lives here.

A bot chat has no terminal and cannot wait on one across turns. Orca wakes a bot only by a message, and a supervised worker's report is the one message that says work has ended. The terminal-only rule never reached a bot in any case: a bot chat sets none of `ORCA_TERMINAL_HANDLE`, `ORCA_PANE_KEY` or `ORCA_TAB_ID`, so the door did not fire and the bot read no page. A canary bot's transcripts on disk, on Orca 1.4.271, show every repo worker run through `orca orchestration worker-start` for that reason, and 91 `worker_done` messages received.

## The line

Orca carries work and wakes the bot. It never decides that work is done.

- `worker_done` is transport. Work is done only after hStack's own evidence and a check by a worker that did not write it.
- The evidence folder is the record. An item holds a status and a pointer to that folder, and proves nothing.
- A bot reads repositories and edits none. Every change, of any size, goes to a worker in its own worktree.
- A blocking question to the owner goes on the task's item, so it survives a dead turn.
- Orca Runs, task DAGs, decision gates and the coordinator loop stay skipped.

## Who asked

A bot can be woken by its owner typing in its chat, by another agent's mail, by a schedule, by a connector event and by anyone holding a webhook URL. A handoff and a worker's report arrive as mail with a `From:` header, observed on Orca 1.4.271. A schedule, an event and a webhook run are unobserved, so they are treated the same way. A bot pushes and opens a PR only when the owner typed the go-ahead in the bot's own chat for that job. A run started any other way holds: it saves the PR title and body locally and reports the paths. A bot never merges and never releases. This follows the consumer project's rule that publishing needs the owner's word; it adds no gate of the page's own.

## What a bot chat gets that a pane does not

- **A second door test.** The hook and the written check also fire when `ORCA_BOT_TOOLS_TOKEN` is set. A bot chat is a session with the token set and `ORCA_TERMINAL_HANDLE`, `ORCA_PANE_KEY` and `ORCA_TAB_ID` all unset, as observed on Orca 1.4.271. A session with the token and any of the three is a pane and reads the Orca page. They test that the token is set and never print it, and so does the hosts index line that names the test.
- **Two files from the hook.** A leading `/hstack:hugues-mode` does not expand in a handoff or an automation body, and the Skill tool refuses the mode. So in a bot chat the hook names the hosts index and the mode file. ADR 0004 let the hook name one file; a bot chat is the exception.
- **Bypass by the owner's act.** Orca starts a bot and its workers with full access, observed on Orca 1.4.269 as a canary bot's `bypassPermissions` and `--dangerously-skip-permissions` on an Orca worker terminal (from `ps`), so a permission card has nobody to answer it. Creating a lead bot is the owner's approval of that for the bot and its workers. The page grants nothing itself.

## What changes for a pane

One thing. A worker a bot starts is an Orca pane, so it reads the Orca page, whose Skip line names `worker_done`. That worker sends the `worker_done` its dispatch asks for, because the bot is woken by nothing else. It still starts and settles nothing of its own through Orca, and the Orca page does not tell it to ask. A worker question that arrives anyway is answered by the bot. A bot's worker must be a pane. Orca's source says a worker started as a chat gets `ORCA_TERMINAL_HANDLE` (1.4.271), so whether such a worker would read a page is unobserved, and the bot reports a `worker-start` receipt whose `mode` is not `terminal` as a gap.

## Considered options

- **Keep bots terminal-only.** Nothing wakes the bot when a worker ends, so a bot could only run work inside one long turn, and a dead turn loses the run.
- **Drop terminal-only for panes too.** It reverses #50 for every Orca session to solve a problem only a bot has.

## Consequences

- Observed on Orca 1.4.271 with a Claude Code bot and Claude Code workers. A claim stamped 1.4.269 was seen while the app was updating to 1.4.271, so it may be either build. A Codex or omp bot, a Codex worker started by a bot, a chat worker, a bot group room and a plain Orca chat that is not a bot are unobserved. So is whether a pane that a bot started carries the bot token. If it did, the worker would still be a pane, because a session with the token and a pane variable reads the Orca page.
- A worker in a repo worktree does not inherit the deny file in the bot's home (observed on 1.4.269). `worker-start` has no flag for agent arguments (help, 1.4.271), and Orca strips `--disallowedTools` from a chat's configured arguments (source, 1.4.271). Whether one reaches a worker pane is unobserved, although a `--disallowedTools` flag on a `claude` command run in a pane hid the tools on 1.4.269. A worker's tool deny is therefore not enforced by hStack. The brief states the ban in words, and the owner may add a deny rule to their own user settings.
- Model, effort and permission mode of a bot are set only in the Orca app, and a bot is created only by the owner's click. hStack ships text for the owner to use and no setup skill.
- The proof on Orca 1.4.277 is a later step. Until it runs, every lane there is a gap.
