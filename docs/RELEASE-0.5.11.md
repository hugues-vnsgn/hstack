# hStack 0.5.11

## What's new

Version 0.5.11 moves the pin from upstream 0.15.43 to 0.15.48 (`9e278fe4`), adds
a page and a kit for running hStack in an Orca bot, and fixes the session-start
hook on Windows. Upstream changed 15 files, added 3 and removed none, and the
ledger grew to 554 rows. The skill count goes from 63 to 64, and 63 of them are
user-only. The 22 generic playbooks, the four mobile playbooks, the native build
and test helpers and the agents are unchanged.

- **`/reframe`, new from upstream.** A user-only skill that teaches the expert
  words for what you are building. It gives 8 to 12 terms, ranked by how much
  each would change what gets built, borrows terms from 2 or 3 neighboring fields
  that solved the same problem, names what you did not mention, and rewrites your
  description with the new words. It opens every link it cites and cuts any it
  cannot confirm. hStack ports the body unchanged, adds the host invocation
  contract and a Codex policy file, and lists it in `hugues-help` and guide
  chapter 2.
- **statechart on native Windows.** Upstream's fix comes over verbatim. The group
  kill moves to `kill.ts` and the janitor to `janitor.ts`, so no script spawns
  `/bin/sh`, TLC's `\r\n` line ends are read, and `SKILL.md` says to run Node
  directly on native Windows. This is upstream's answer to issue
  [#164](https://github.com/hugues-vnsgn/hstack/issues/164), and it replaces
  PR #165.
- **Upstream's Gemini seat change is not ported.** Upstream moves its panel's
  Gemini seat to `gemini-4-neon-xhigh` and has setup migrate an old Gemini entry.
  hStack's panels seat Fable, Opus and a GPT model and carry no Gemini seat, so
  `arena`, `hugues-mode` and `setup-hstack` keep their 0.5.10 bytes. The ledger
  rows say so.
- **The door finds an Orca bot chat (#169).** A bot chat sets none of the three
  Orca pane variables, so the door never fired there and a bot read no page. The
  session-start hook and the written check in `host-workers.md` now also match
  when Orca's bot token is set and no pane variable is. They test only that it is
  set and never print it. In a bot chat the hook names the mode file beside the
  hosts index, and ADR 0007 gives the reason. A session with the token and a pane
  variable is still a pane.
- **The Orca bot page.** [`orca-bot.md`](../plugin/adapters/hosts/orca-bot.md)
  says how a lead bot starts workers with Orca's `worker-start`, ends its turn and
  is woken by their `worker_done` mail. That mail is transport and never proof:
  done needs the evidence folder and a check by a fresh worker that did not write
  the code. The bot reads repos and edits none, puts a blocking question on the
  task's Orca item, and pushes or opens a PR only when the owner typed the
  go-ahead in the bot's own chat for that job. It never merges and never
  releases. [ADR 0007](adr/0007-an-orca-bot-uses-supervised-workers-as-transport.md)
  records why a bot uses Orca's supervised workers as transport while a pane
  stays terminal-only. The glossary gains **Bot** and **Bot chat**.
- **The bot kit.** [`docs/orca-bots.md`](orca-bots.md) holds the steps you do by
  hand, the lead SOUL text, the home deny file for the Gmail, Google Drive, Google
  Calendar and Slack connector tools, and the Orca app settings. hStack ships no
  setup skill and no coder or checker bot.
- **Corrected after the Orca 1.4.277 proof (#172).** All five `worker-start`
  receipts seen on 1.4.277 said `mode: structured`, and no option chooses the
  mode, so the page no longer calls a receipt that is not `terminal` a gap.
  Orca's own wrapper tells a structured worker to send `worker_done`, so that
  mail does not show hStack loaded. The brief now asks each worker to list the files it read
  before the task, and the bot reports a worker whose list lacks `worker.md`, the
  mode file, the hosts index and its page as a gap. That list is the worker's own
  statement, and the page relies on the independent reviewer. A lost worker is
  retried once by a send to the same dispatch. The kit now puts the SOUL and the
  deny file in place first, sends no task to the chat Orca opens at creation,
  starts a new chat, and checks `SOUL.md` after the first run. The SOUL gains two
  Never lines: the bot never rewrites its SOUL unless the owner asks in the chat,
  and it never offers to break one of its own Never lines.
- **The session-start hook on Windows (#163).** The hook now runs `python3`
  before trusting it. On Windows, `python3` can resolve to the Microsoft Store
  stub, which `command -v` finds and which exits 49 when run, so the hook failed
  in an Orca session there. A stub now falls through to the hook's shell
  encoder.
- **README and user guide.** The README gains "Run hStack inside Orca", for a
  pane and for a bot. The HTML user guide gains section 22, "Run the team in
  Orca", with Orca bot rows in troubleshooting and the appendices. Its sections
  22 to 24 become 23 to 25, and their anchors are unchanged.

## Upgrade

Update or reinstall the plugin on each host, as in the
[0.5.8 upgrade](RELEASE-0.5.8.md#upgrade), then restart the Claude Code process
and start fresh sessions. Check that the resolved payload reports 0.5.11.

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

`setup-hstack` is unchanged, so a project that already ran setup keeps its
`.hstack/models.md` as it is.

The Bun install key is unchanged from 0.5.10: neither `package.json` nor
`bun.lock` in `hugues-mode/scripts/` changed.

An Orca pane needs nothing new. To run hStack in an Orca bot, follow the
[bot kit](orca-bots.md). You set the bot up by hand in the Orca app, and nothing
migrates. If you set up a bot from the kit on `main` before this release, copy
the kit's SOUL text into its `SOUL.md` again to get the two new Never lines.

## Validation

Static checks establish source and wiring contracts only. They ran at the
release head on macOS with Python 3.15.2 and Node 22.23.4.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 605 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 64 skills | Plugin layout, manifests, installed payload and the upstream-name guard. |
| `python3 scripts/check_core.py` | PASS, 554 archive files, 22 core playbooks | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 554 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

The `hugues-mode` helper and its Bun suite are unchanged since 0.5.10 and were
not rerun. An independent review of the 0.15.48 merge found the statechart
scripts and the provenance archive byte-equal to upstream `9e278fe4`, and found
that only the Gemini-seat hunks were left out. The statechart CLI and message
tests, which replay committed TLC output, ran once in a scratch copy on Node
22.23.4: 166 of 167 passed. The one failure, a relative-symlink launcher case,
fails the same way on the 0.15.43 upstream bytes on that machine.

### The Windows hook failure, observed before the fix

On Windows 11, with Claude Code in an Orca 1.4.261 pane, the installed 0.5.8
hook printed the Store message and exited 49. With the Store aliases folder
removed from `PATH`, it printed valid JSON. A new test case puts a `python3` stub
that exits 49 first on `PATH`: it failed before the fix and passes after it.

### The Orca bot proof, observed

Five lanes of issue [#168](https://github.com/hugues-vnsgn/hstack/issues/168) ran
on Orca 1.4.277 on 2026-11-27. They used one throwaway Claude Code bot on
`claude-opus-5-5` at high effort, Claude Code workers, one throwaway repo with a
local bare remote, and hStack `main` at `e6f687a` installed in Claude Code. The
tasks were tiny. Each lane was judged from the bot's and the workers'
transcripts, not from the bot's own report. The verdicts and transcripts stay in
the maintainer's private store.

The proof ran before #172. The page text that #172 added is defined, not yet
observed: the structured-worker wording, the worker's list of files read, the
kit's new step order and the two new SOUL Never lines.

- **Lane 1, the door.** In the bot chat, Orca's bot token was set and the three
  pane variables were unset. hStack's session-start hook ran, and its message
  named the hosts index and the mode file. The bot read the mode file, the index
  and the bot page. `CLAUDE_PLUGIN_ROOT` was unset in the bot's own Bash, yet the
  hook resolved its root.
- **Lane 2, an owner-typed run.** A `/hstack:hugues-mode` task that the owner
  typed in the bot's chat expanded and loaded the mode. The repo was not yet an
  Orca project. Asked to register it, the bot refused, cited the page's ban on
  `orca repo add`, and put the question on an item as needs-you. After the owner
  registered the repo and answered in the chat, the run went to its end. The bot
  started an implementer on the repo's `feature` role line and a fresh reviewer
  on its `judgment and prose` line, each in its own worktree. Two `worker_done`
  messages woke the bot. It checked the head and the tree itself, edited no repo
  file and pushed nothing: the commit is on a local branch, and the remote holds
  `main` alone. It saved its report as one HTML file in its chat scratch folder.
- **Lane 3, a handoff run.** The handoff body held no path. The bot read the
  hosts index, the mode file and the bot page before it acted. It started an
  implementer and a fresh reviewer with `worker-start`, each in its own
  `new-child` worktree, on the repo's role lines, and each worker's transcript
  confirms its model. Both workers read `worker.md`. Two `worker_done` messages
  woke the bot, and it reran the suite itself, 6 of 6 passing, before it closed
  the item. It edited no repo file and pushed nothing. Both receipts said
  `mode: structured`, which the page at `e6f687a` called a gap. The bot reported
  it as the page asked, and #172 corrected the page. This lane ran under a SOUL
  the bot had written itself, not the kit's.
- **Lane 4, a lost worker.** The worker's Claude Code process was killed twice
  with SIGKILL. Each loss reached the bot as an `escalation` message, the first
  "Worker exited without reporting" and the second "Worker stopped on an error
  without reporting". The bot told the owner that nothing was written or checked,
  and retried once by a send to the same dispatch. After the second loss it
  started nothing more, set the item to needs-you and reported the work as lost.
  Orca's `worker-list`, run from outside the bot, still showed the dispatch as
  ready, with outcome in progress and liveness exited, and the bot did not take
  that for done.
- **Lane 7, the deny file.** With the kit's deny file in the bot's home, the
  Gmail, Google Drive and Google Calendar tool names occur nowhere in the bot
  chat's transcript, while other connector tools do. A Claude Code session on the
  same account outside the bot lists all three. The Google Drive server's
  instructions still appeared in the bot's context.
- **A kit defect.** The chat Orca opened when the bot was created wrote its own
  short SOUL over the kit text within a minute of its first task. After the text
  was restored, Orca pushed it into the open chat on its next wake, and the rest
  of lane 2 ran under the kit SOUL. #172 changed the kit's step order and added a
  Never line for it.

## Known gaps

- The Orca bot proof ran against `main` at `e6f687a`, before #172. The corrected
  page text is defined, not yet observed: the structured-worker wording, the
  worker's list of files read, the kit's new step order and the two new SOUL
  Never lines.
- Orca bot lanes not run on 1.4.277: a `worker_done` that arrives while the
  bot's turn is dead (lane 5), `new-child` under a custom worktree base path
  (lane 8), and saving a PR title and body locally (the second half of lane 6).
  No run asked for a PR, and the runs pushed nothing.
- Orca bots, unobserved: the Slack entry of the deny file, because the account
  has no Slack tool; a Codex or omp bot; a Codex worker started by a bot; bot
  groups; a plain Orca chat that is not a bot; and `worker-start --retry-of` on
  1.4.277.
- The proof used one bot on one machine, Claude Code only, on tiny tasks.
- hStack does not enforce a worker's tool deny. The bot's home deny file does not
  reach a repo worktree, and the brief states the ban in words.
- The fixed session-start hook is unobserved on Windows. The machine where the
  failure was seen has since turned off the Store aliases, so it no longer
  reproduces there.
- No host has run `/reframe`.
- No statechart run on native Windows was observed, so issue #164 stays open. The
  full statechart suite needs TLC and Java and did not run.
- The 0.15.48 provenance archive was built with Python 3.12. Python 3.15's zlib
  does not reproduce the earlier archives byte for byte.
- No Codex or Cursor session ran for this release.
- The update from 0.5.10 to 0.5.11 is unobserved on every host.
- The gaps listed in the [0.5.10 notes](RELEASE-0.5.10.md#known-gaps) carry over
  unless this page says otherwise.
