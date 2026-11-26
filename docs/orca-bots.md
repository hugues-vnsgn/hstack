# Orca bots

This is the kit for running hStack in an Orca bot. You read it and do the steps by hand. hStack ships no setup skill, and no coder bot or checker bot: the lead bot starts workers, and a fresh worker does the independent check.

A bot chat has no terminal. hStack's [Orca bot page](../plugin/adapters/hosts/orca-bot.md) says how the bot starts workers, waits for them and reports. [ADR 0007](adr/0007-an-orca-bot-uses-supervised-workers-as-transport.md) gives the reason, and issue #168 holds the spec.

Everything here was observed on Orca 1.4.271 with a Claude Code bot and Claude Code workers, unless a line says otherwise. A Codex or omp bot, a Codex worker, a bot group room and any later Orca build are unobserved.

## Steps

1. Register the repo in Orca yourself. The bot never runs `orca repo add`.
2. If the repo needs its worktrees in one place, set the base path once: `orca project setup-update --setup <setup-id> --worktree-base-path <path>`. A bot's worktree was made under `~/orca/workspaces/<repo>/<name>` (observed on 1.4.271). Whether `new-child` follows a custom path is unobserved.
3. In the Orca app, create one lead bot for this project and name it for the project. Creating it is your approval of full access for the bot and its workers.
4. Put the SOUL text below in the bot's `SOUL.md`.
5. Put the deny file below in the bot's home folder.
6. Set the app settings below.
7. Start a new chat. The session start message should name the hosts index and the mode file. hStack's door calls a session a bot chat when `ORCA_BOT_TOOLS_TOKEN` is set and `ORCA_TERMINAL_HANDLE`, `ORCA_PANE_KEY` and `ORCA_TAB_ID` are all unset, so a pane gets the index alone. That is unobserved until the proof run. If the message names no mode file, the bot has to say so and stop, as its SOUL says.

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

Orca starts the bot's Claude Code with user, project and local settings (source, 1.4.271), so this file applies to the bot chat. On Orca 1.4.269 it removed the Gmail, Drive and Calendar tools from a bot chat that ran with full access. The Slack entry is unobserved, because that bot had no Slack tool.

The file does not reach a worker. A worker runs in a repo worktree, where this file does not apply: a pane a bot started there listed the Gmail tools (observed on 1.4.269). `worker-start` has no flag for agent arguments (help, 1.4.271), and Orca strips `--disallowedTools` from a chat's configured arguments (source, 1.4.271). Whether a flag reaches a worker pane is unobserved, although a `--disallowedTools` flag on a `claude` command run in a pane hid the tools on 1.4.269. So hStack states the ban in each worker's brief and does not enforce it. To enforce it, add the same four entries to `permissions.deny` in your own `~/.claude/settings.json`. That applies to every Claude Code session you run, and it is unobserved here.

## Settings in the Orca app

Orca sets a bot's model, effort and permission mode only in the app. A bot is created only by your click.

| Setting | Value | Why |
|---|---|---|
| Model and effort | The Claude value of the `judgment and prose` line in the repo's `.hstack/models.md`, at that line's effort. | The lead plans, briefs and judges. Its workers take their own role lines. |
| Permission mode | Full access, which is the default for a new bot (observed on 1.4.269 as `bypassPermissions`). | A mode that asks would stop the run on a card that nobody answers, which is unobserved in a bot. The page grants no permission. |
| Look around | Off. | It runs on a schedule, about every 4 hours on a canary bot (observed on 1.4.271), and each run costs tokens. |
| Reports | Nothing to set. The SOUL text above asks for one `::orca-visual` HTML file. | Orca's chat visuals work when `ORCA_CHAT_SCRATCH_DIR` is set, and it was set in a bot chat (observed on 1.4.271). Unobserved: whether the app has a switch for it. |

## Not covered

- Bot groups, Orca automations as schedulers, remote or paired computers and any bot other than the lead.
- A worker started as a chat instead of a pane. The bot reports a `worker-start` receipt whose `mode` is not `terminal` as a gap. Orca's source says such a worker gets `ORCA_TERMINAL_HANDLE` (1.4.271), so whether it reads a page is unobserved.
- Proof on Orca 1.4.277: it runs after this lands, with the lanes in issue #168.
