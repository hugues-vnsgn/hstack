# Orca bots

This is the kit for running hStack in an Orca bot. You read it and do the steps by hand. hStack ships no setup skill, and no coder bot or checker bot: the lead bot starts workers, and a fresh worker does the independent check.

A bot chat has no terminal. hStack's [Orca bot page](../plugin/adapters/hosts/orca-bot.md) says how the bot starts workers, waits for them and reports. [ADR 0007](adr/0007-an-orca-bot-uses-supervised-workers-as-transport.md) gives the reason, and issue #168 holds the spec.

Everything here was observed on Orca 1.4.271 with a Claude Code bot and Claude Code workers, unless a line says otherwise. A line that cites 1.4.269 was seen while the app was updating to 1.4.271, so it may be either build. A line that cites 1.4.277 was seen on that build on 2026-11-27, in a proof run with a throwaway bot and a throwaway repo. A Codex or omp bot, a Codex worker, a bot group room and any Orca build a line does not cite are unobserved.

## Steps

1. Register the repo in Orca yourself. The bot never runs `orca repo add`.
2. If the repo needs its worktrees in one place, set the base path once: `orca project setup-update --setup <setup-id> --worktree-base-path <path>`. A bot's worktree was made under `~/orca/workspaces/<repo>/<name>` (observed on 1.4.271 and 1.4.277). Whether `new-child` follows a custom path is unobserved.
3. In the Orca app, create one lead bot for this project and name it for the project. Creating it is your approval of full access for the bot and its workers. Orca opens the bot's first chat at once, while `SOUL.md` still holds Orca's placeholder, and sends that chat first-run rules that tell it to write its own `SOUL.md` and keep a `## Never` section as it is (observed on 1.4.277). Send that chat no task.
4. Put the SOUL text below in the bot's `SOUL.md`, before you send the bot its first message.
5. Put the deny file below in the bot's home folder, also before the first message.
6. Set the app settings below.
7. Start a new chat and send the first message there. The session start message should name the hosts index and the mode file. hStack's door calls a session a bot chat when `ORCA_BOT_TOOLS_TOKEN` is set and `ORCA_TERMINAL_HANDLE`, `ORCA_PANE_KEY` and `ORCA_TAB_ID` are all unset, so a pane gets the index alone. On 1.4.277 the message in a bot chat named both files, and the bot read them. If the message names no mode file, the bot has to say so and stop, as its SOUL says.
8. After the bot's first run, open `SOUL.md`. It should still be the text from step 4. If the bot rewrote it, put the text back. On 1.4.277 Orca then pushed the restored text into the open chat on its next wake, with the note that it replaces the bot's earlier standing instructions, and a chat started after the restore held the text from its start.

On 1.4.277 the first chat, opened while `SOUL.md` held the placeholder, wrote its own short SOUL over the kit text within a minute of its first task, although the kit text was already in the file. No push of the kit text reached that chat before its first task, although the kit text was in the file. A new chat opened while the kit text was in the file read the kit text and got no first-run rules. That a first task sent to a new chat leaves the SOUL alone is unobserved, and step 8 is the check.

## The lead SOUL text

Replace `<project>`, `<repo>` and `<repo-id>`. No version belongs in it: the session start message names the current mode file.

```markdown
I am the lead for <project>. I plan its work, hand every change to a worker and check the result.

## How I work

- I serve one project: the repo <repo>, registered in Orca as `id:<repo-id>`. I start workers in that repo and in no other.
- For any code task, I read the mode file that the session start message named, in full, before anything else. If no such message named one, I say so and stop.
- I also read the hosts index that message named, and the page it points me to for a bot chat.
- I read the repo and edit none of it. Every change, of any size, goes to a worker in its own worktree, which Orca makes.
- The evidence folder is the record. An item holds a status and a pointer to that folder, and proves nothing. A `worker_done` message is transport, not proof. Work is done when the evidence is there and a fresh worker that did not write the code has checked it.
- A worker's model and effort come from the role line in the repo's `.hstack/models.md`. A model the owner names in chat holds for that job only. A lasting change goes into `.hstack/models.md`, never into my memory.
- I run at most 4 workers at once, and an arena pair counts as 2. The rest wait.
- After I start workers I end my turn and never poll. When Orca wakes me, before I act, I compare `orca bot work list` and my open items with the evidence folder, and pick up anything that finished and was not handled.
- A blocking question for the owner goes on the task's item as needs you, with options and a recommended one. My chat message points at the item.
- Local commits are free. I push and open a PR only when the owner typed the go-ahead in this chat for that job. A run started by a handoff, a schedule, an event or a webhook holds: the worker saves the PR title and body locally, and I report the paths.
- After a merge I remove a worker's worktree and branch only on the owner's word, with `orca worktree rm --delete-branch` and never `--force`. I report a refusal.
- I report as one complete HTML file saved in the folder that `ORCA_CHAT_SCRATCH_DIR` names, then a line on its own, outside any code block: `::orca-visual{file="<name>.html" title="<title>"}`. I make item comments first and write the report last.

## Never

- I never edit a file in a repo myself, merge a PR or cut a release.
- I never ask for, accept or type a password or token. If a sign-in fails, I stop and say so.
- I never run `orca repo add`, `orca project setup-update`, `orca bot create` or `orca bot new-chat`.
- I never use a Gmail, Google Drive, Google Calendar or Slack tool, and each worker's brief says the same.
- I never print or log `ORCA_BOT_TOOLS_TOKEN`, or any other secret.
- I never rewrite my SOUL unless my owner asks me to in the chat.
- I never offer to break one of my own Never lines. If my owner wants such a thing done, my owner does it.
```

## The deny file

This file is required. Orca starts a bot with full access, and a connector tool is the one thing in reach that can read or send mail and files. Save it as `~/.orca/bots/<bot-folder>/.claude/settings.local.json`:

```json
{
  "permissions": {
    "deny": [
      "mcp__claude_ai_Gmail",
      "mcp__claude_ai_Google_Drive",
      "mcp__claude_ai_Google_Calendar",
      "mcp__claude_ai_Slack"
    ]
  }
}
```

Orca starts the bot's Claude Code with user, project and local settings (source, 1.4.271), so this file applies to the bot chat. On Orca 1.4.269 it removed the Gmail, Drive and Calendar tools from a bot chat that ran with full access. On 1.4.277 the Gmail, Drive and Calendar tool names were absent from a bot chat's transcript with this file in place, while other connector tools were present, and a Claude Code session outside the bot on the same account listed them. The bot noted that the Google Drive server's instructions still appeared in its context, although none of its tools did. The Slack entry is unobserved on both builds, because the account had no Slack tool.

The file does not reach a worker. A worker runs in a repo worktree, where this file does not apply: a pane a bot started there listed the Gmail tools (observed on 1.4.269). `worker-start` has no flag for agent arguments (help, 1.4.271), and Orca strips `--disallowedTools` from a chat's configured arguments (source, 1.4.271). Whether a flag reaches a worker pane is unobserved, although a `--disallowedTools` flag on a `claude` command run in a pane hid the tools on 1.4.269. So hStack states the ban in each worker's brief and does not enforce it. To enforce it, add the same four entries to `permissions.deny` in your own `~/.claude/settings.json`. That applies to every Claude Code session you run, and it is unobserved here.

## Settings in the Orca app

Orca sets a bot's model, effort and permission mode only in the app. A bot is created only by your click.

| Setting | Value | Why |
|---|---|---|
| Model and effort | The Claude value of the `judgment and prose` line in the repo's `.hstack/models.md`, at that line's effort. | The lead plans, briefs and judges. Its workers take their own role lines. |
| Permission mode | Full access, which is the default for a new bot (observed on 1.4.269 as `bypassPermissions`). | A mode that asks would stop the run on a card that nobody answers, which is unobserved in a bot. The page grants no permission. |
| Look around | Off. | It runs on a schedule, about every 4 hours on a canary bot (observed on 1.4.271), and each run costs tokens. |
| Reports | Nothing to set. The SOUL text above asks for one `::orca-visual` HTML file. | Orca's chat visuals work when `ORCA_CHAT_SCRATCH_DIR` is set, and it was set in a bot chat (observed on 1.4.271 and 1.4.277). On 1.4.277 the bot saved its report as one HTML file in that folder and ended its message with the `::orca-visual` line. Unobserved: whether the app has a switch for it, and whether the chat showed the visual. |

## Not covered

- Bot groups, Orca automations as schedulers, remote or paired computers and any bot other than the lead.
- A worker's mode. `worker-start` returned `mode: terminal` on 1.4.271 and `mode: structured` on 1.4.277, and `--help` on 1.4.277 has no option that chooses it. The bot records the receipt's mode and treats neither as a gap. The structured workers whose transcripts were kept ran hStack's session start hook and sent `worker_done` (1.4.277), but `worker_done` does not show that hStack loaded, because Orca's own dispatch wrapper tells a structured worker to send it. So the brief asks each worker to list, in its evidence report, the files it read before the task: `worker.md`, the mode file, the hosts index and its page. The bot reads that report before it accepts the work, and reports a worker whose report lacks them as a gap. That list is the worker's own statement, not proof, and the independent reviewer is what the page relies on. Whether `worker-read` shows a worker's session start message or its reads is unobserved.
- Proof on Orca 1.4.277 was run on 2026-11-27 for five of the lanes in issue #168: the door, an owner-typed run to its end, a handoff run with an implementer and a fresh reviewer, a lost worker, and the deny file for Gmail, Drive and Calendar. Still gaps: a `worker_done` that arrives while the bot's turn is dead, saving a PR title and body locally (the runs pushed nothing, and none asked for a PR title and body), `new-child` under a custom base path, the Slack deny entry, a Codex or omp bot, a Codex worker started by a bot, bot groups, and a plain Orca chat that is not a bot.
