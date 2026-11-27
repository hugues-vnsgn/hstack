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

A bot can be woken by its owner typing in its chat, by another agent's mail, by a schedule, by a connector event and by anyone holding a webhook URL. A handoff and a worker's report arrive as mail with a `From:` header, observed on Orca 1.4.271 and 1.4.277. A schedule, an event and a webhook run are unobserved, so they are treated the same way. A bot pushes and opens a PR only when the owner typed the go-ahead in the bot's own chat for that job. A run started any other way holds: it saves the PR title and body locally and reports the paths. A bot never merges and never releases. This follows the consumer project's rule that publishing needs the owner's word; it adds no gate of the page's own.

## What a bot chat gets that a pane does not

- **A second door test.** The hook and the written check also fire when `ORCA_BOT_TOOLS_TOKEN` is set. A bot chat is a session with the token set and `ORCA_TERMINAL_HANDLE`, `ORCA_PANE_KEY` and `ORCA_TAB_ID` all unset, as observed on Orca 1.4.271 and 1.4.277. A session with the token and any of the three is a pane and reads the Orca page. They test that the token is set and never print it, and so does the hosts index line that names the test.
- **Two files from the hook.** A leading `/hstack:hugues-mode` does not expand in a handoff or an automation body, and the Skill tool refuses the mode. So in a bot chat the hook names the hosts index and the mode file. ADR 0004 let the hook name one file; a bot chat is the exception. Observed on Orca 1.4.277: the hook ran in a bot chat, its message named both files, and the bot read the mode file, the index and the bot page. `CLAUDE_PLUGIN_ROOT` was unset in the bot's own Bash, so the paths come from the hook's message. A `/hstack:hugues-mode <task>` that the owner typed in the bot's chat expanded and loaded the mode, and the owner-typed run went to its end. A handoff body that starts with the command is unobserved.
- **Bypass by the owner's act.** Orca starts a bot and its workers with full access, observed on Orca 1.4.269 as a canary bot's `bypassPermissions` and `--dangerously-skip-permissions` on an Orca worker terminal (from `ps`), so a permission card has nobody to answer it. Creating a lead bot is the owner's approval of that for the bot and its workers. The page grants nothing itself.

## What changes for a worker

One thing. A worker a bot starts reads the Orca page, whose Skip line names `worker_done`. That worker sends the `worker_done` its dispatch asks for, because the bot is woken by nothing else. It still starts and settles nothing of its own through Orca, and the Orca page does not tell it to ask. A worker question that arrives anyway is answered by the bot.

The first version of this ADR called every such worker a pane, and made a `worker-start` receipt whose `mode` was not `terminal` a gap. Orca 1.4.271 returned `mode: terminal`. Orca 1.4.277 returned `mode: structured` and a terminal named `structworker_<uuid>` for all five starts seen, and `worker-start --help` there has no option that chooses the mode. The four structured workers whose transcripts were kept ran hStack's `SessionStart` hook and got the ADE message, which has no bot sentence. All four read `worker.md` and sent `worker_done`, which woke the bot. Three read the Orca page, and the fourth, a reviewer, read the hosts index and not the page. One worker's own check counted exactly one of the three pane variables set, and which one was not recorded. So the page no longer requires `terminal`, and the bot records each receipt's mode in its evidence.

The gap test cannot be `worker_done`. Orca's own dispatch wrapper tells a structured worker to send it, so it does not show that hStack loaded. The page gives the bot one check it can make: the brief asks the worker to list, in its evidence report, the files it read before the task, and the bot reports a worker whose report lacks `worker.md`, the mode file, the hosts index and its page as a gap. That list is the worker's own statement, not proof, and the independent reviewer is what the page relies on. Whether `worker-read` shows a worker's session start message or its reads is unobserved.

## Considered options

- **Keep bots terminal-only.** Nothing wakes the bot when a worker ends, so a bot could only run work inside one long turn, and a dead turn loses the run.
- **Drop terminal-only for panes too.** It reverses #50 for every Orca session to solve a problem only a bot has.

## Consequences

- Observed on Orca 1.4.271 and 1.4.277 with a Claude Code bot and Claude Code workers. A claim stamped 1.4.269 was seen while the app was updating to 1.4.271, so it may be either build. A Codex or omp bot, a Codex worker started by a bot, a bot group room and a plain Orca chat that is not a bot are unobserved. So is whether a worker that a bot started carries the bot token. If it did, the worker would still read the Orca page, because a session with the token and a pane variable is a pane.
- A worker in a repo worktree does not inherit the deny file in the bot's home (observed on 1.4.269). `worker-start` has no flag for agent arguments (help, 1.4.271), and Orca strips `--disallowedTools` from a chat's configured arguments (source, 1.4.271). Whether one reaches a worker pane is unobserved, although a `--disallowedTools` flag on a `claude` command run in a pane hid the tools on 1.4.269. A worker's tool deny is therefore not enforced by hStack. The brief states the ban in words, and the owner may add a deny rule to their own user settings. On 1.4.277 the deny file did what it did on 1.4.269 for the bot chat: the Gmail, Drive and Calendar tool names were absent from the chat's transcript while other connector tools were present. The Slack entry is unobserved, because the account has no Slack tool.
- Model, effort and permission mode of a bot are set only in the Orca app, and a bot is created only by the owner's click. hStack ships text for the owner to use and no setup skill.
- A bot's first chat can rewrite its SOUL. Orca opens that chat when the owner creates the bot and sends it first-run rules that tell it to write `SOUL.md` and to keep a `## Never` section as it is. On 1.4.277 that chat wrote its own short SOUL over the kit text within a minute of its first task, although the kit text was already in the file and no push of it had reached that chat. After the text was restored, Orca pushed it into the open chat on its next wake, as a note that it replaces the bot's earlier standing instructions, and a chat started after the restore held the text from its start. The kit now keeps the first task out of the first chat, adds a Never line against the rewrite, and has the owner check `SOUL.md` after the first run. That the new order stops the rewrite is unobserved.
- The proof ran on Orca 1.4.277 on 2026-11-27, with a throwaway bot and a throwaway repo, a Claude Code bot and Claude Code workers, and hStack main at e6f687a installed. It observed the door, an owner-typed `/hstack:hugues-mode` run to its end, a handoff run with an implementer and a fresh reviewer, a lost worker, and the deny file for Gmail, Drive and Calendar. In the owner-typed run, the ask to register a repo was refused. The owner's message already said the Orca page bars it, and the bot's item still offered the owner an option to have the bot run it anyway. The owner ruled that the bot never offers to break one of its own Never lines, so the SOUL text in the kit says so: if the owner wants such a thing done, the owner does it. That rule is defined, not yet observed. The gaps are a `worker_done` that arrives while the bot's turn is dead, saving a PR title and body locally (the runs pushed nothing, and none asked for them), `new-child` under a custom base path, the Slack deny entry, a Codex or omp bot, a Codex worker started by a bot, bot groups, and a plain Orca chat that is not a bot.
