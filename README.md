# hStack

hStack gives Claude Code, Codex and Cursor a set of workflows for investigating, changing and checking code. It adds optional guidance for Swift/iOS, Kotlin/Android, Kotlin Multiplatform (KMP) shared logic and Compose Multiplatform (CMP) shared UI. Your app stays in its own repository.

Setup starts the code, prose and judgment roles on `claude-opus-5-5` at `xhigh`
and runs review panels at `high`. No role runs above `xhigh`, and
`claude-fable-5-2` runs only when you ask for it or after two failed Opus runs.
Setup's verification offer is optional for every project, and mobile is one
optional adapter. The pin is upstream 0.15.48 and the skill count is 64: the new
user-only `reframe` skill teaches the expert words for what you are building.
The tree has 22 generic playbooks and four mobile ones. Orchestrate and the plan
checker are removed. A Cursor user installs the plugin, sees its skills and runs
`/hugues-mode`, `/hugues-help` and
`/setup-hstack` in the Cursor IDE. A `.cursor-plugin/` manifest pair points at
the same `plugin/skills/` and `plugin/agents/`, so one tree serves all three
hosts. Start a run by typing
`/hstack:hugues-mode` in Claude Code or `$hugues-mode` in Codex. The release
keeps the native helpers unchanged. The [0.5.11 release notes](docs/RELEASE-0.5.11.md) record
upgrade steps, checks and remaining gaps. hStack supports Swift/iOS, Kotlin/Android, KMP
and CMP development through its optional mobile adapter. A complete journey on a real
consumer project remains unobserved on any host. The plugin remains `hstack`. Its
commands start with `/hstack:`, and the setup skill is `setup-hstack`.
The 0.5.0 release has 57 public skills, 23 generic playbooks, two agents and four mobile playbooks.
Version 0.5.1 added two authored user-only language skills. Version 0.5.11 adds upstream's `reframe` and has 64 in total. Each skill owns one canonical `SKILL.md`.
Against 0.3.0's 50 skills, 0.4.0 merges upstream 0.15.25 and adds four user-only
skills. After 0.4.0, hStack bundles `deslop`, `control-cli` and `control-ui` from
Cursor's `cursor-team-kit`. Upstream calls these skills but does not ship them.
Exact upstream source remains in a provenance archive outside
runtime discovery. Only `setup-hstack` appears in the host's skill list. You
type `hugues-mode`, and it reads the other skills as files. The published 0.1.0, 0.2.0 and 0.3.0 releases and
their evidence are unchanged.

## Start with Claude Code

For an already installed, signed-in CLI, load this checkout for one session from
your app directory (replace the absolute path):

```sh
claude --plugin-dir "/absolute/path/to/hstack/plugin"
```

Confirm native discovery, then invoke `/hstack:hugues-mode` with a small
read-only request. Session-only package loading is documented host behavior, and
one interactive session of this layout loaded the plugin that way and fired the
router. The [interactive check](docs/router-interactive-check.md) records that session.
The [0.5.0 validation](docs/RELEASE-0.5.0.md#validation) adds a bounded headless
bug-fix run with hooks off and bypassPermissions. Interactive workflow completion
under normal permissions remains unobserved.

## Start with Cursor

Cursor loads hStack from one source only. Pick exactly one route. Either way,
remove the upstream plugin first if you installed it, because 56 of hStack's 64
skill names are shared with it. It has its own folder under
`$HOME/.cursor/plugins/local/`, and the [upstream record](docs/upstream/README.md)
names it.

- **A. You already use hStack in Claude Code.** Install nothing in Cursor.
  Cursor loads hStack from Claude Code's install, so both hosts stay on and
  update together. Remove any `~/.cursor/plugins/local/hstack` copy:

  ```sh
  rm -rf "$HOME/.cursor/plugins/local/hstack"
  ```

  Reload the window. Expected: the `/` list shows hStack's skills once, loaded
  from the Claude plugin cache. Route A is expected until the final check on
  the released plugin proves it; stock Cursor is not observed.

- **B. You don't use Claude Code.** Install hStack as a copy of this
  repository's `plugin/` folder (replace the absolute path):

  ```sh
  src="/absolute/path/to/hstack/plugin"
  dst="$HOME/.cursor/plugins/local/hstack"
  rm -rf "$dst"
  mkdir -p "$dst"
  cp -R "$src"/. "$dst"/
  ```

  Copy rather than symlink. Cursor's own documentation states that a symlink in
  that folder loads only when its target resolves inside it, and that Cursor
  skips one pointing outside it. This repository is outside it.

  Reload the window, then confirm under **Customize → Plugins** that hStack is
  enabled and its components are listed. Type `/hugues-help` in the composer
  to confirm the router answers.

Why one source only: Cursor loads the Claude plugin cache as well as
`~/.cursor/plugins/local/`, and it de-duplicates within one plugin rather than
across plugins, so two sources register every shared skill name twice. Both
halves of that observation come from one lab session on 2026-10-30 with both
sources present, observed in Cursor 3.27.22 with a third-party auth extension:
that session loaded `hstack` from `~/.cursor/plugins/local/hstack`
(`loadUserLocalPlugin`) and from
`~/.claude/plugins/cache/hstack/hstack/0.5.6`
(`loadClaudePlugin hstack@hstack`), and ran the `host-detect.sh` hook once per
copy. Route A keeps only the Claude-cache half; route B keeps only the local
half. Stock Cursor is not observed.

Gaps: stock Cursor is unobserved, and so is the free plan without the
third-party auth extension. A read-only Explore subagent, the paid-feature
skip line, the Swift skill and `recall` are not observed in the Cursor IDE
either. `setup-hstack` and the `hugues-agent` delegate are observed. Route A,
where Cursor loads hStack from Claude Code's install, is expected, not proven:
it is checked at the end, on the released plugin, with hStack on in Claude Code
and no local copy.

A GitHub-marketplace route is also published: a repository root holding
`.cursor-plugin/marketplace.json`, imported through **Dashboard → Plugins & MCPs
→ Add Marketplace → Import from Repo**. That route is unobserved.

## Start with Codex

Use a supported native discovery/invocation route and confirm that `hugues-mode`
appears before using `$hugues-mode`. The 0.5.0 pretest exercised an installed
Codex copy. Updates from 0.4.0 to 0.5.0, 0.5.0 to 0.5.1 and 0.5.1 to 0.5.2
were later observed on both hosts, and both hosts on the maintainer machine
hold 0.5.3 copies that match its tag. Updating from 0.5.3 to 0.5.4, from 0.5.4
to 0.5.5, from 0.5.5 to 0.5.6, from 0.5.6 to 0.5.7, from 0.5.7 to 0.5.8, from 0.5.8 to 0.5.9, from 0.5.9 to 0.5.10 and from 0.5.10 to 0.5.11
remains unobserved. See the [upgrade instructions](docs/RELEASE-0.5.11.md#upgrade). If
`hugues-mode` is unavailable or disabled, stop; direct-reading its body is
not an invocation fallback. The [developer guide](docs/DEVELOPER-GUIDE.md#use-codex)
explains the boundary and a first-task workflow.

## Run hStack inside Orca

Orca is an agent development environment (ADE), not a host. hStack still runs
in Claude Code or Codex, installed as above. Cursor inside Orca is unmapped.
Orca holds the sessions and their worktrees.

- **In an Orca pane**, start Claude Code or Codex in the pane and run
  `hugues-mode` the usual way. There is nothing else to set up. In Claude Code,
  hStack's session-start hook tells the session to read the
  [hosts index](plugin/adapters/hosts/README.md), which sends it to the
  [Orca page](plugin/adapters/hosts/orca.md); Codex loads no plugin hook and
  relies on the written check in [host-workers.md](plugin/adapters/host-workers.md).
  The coordinator runs each worker in its own Orca pane and keeps dispatch,
  completion and verification for itself.

  Status: released in 0.5.6. Coordinators in Orca panes were observed on Orca
  CLI 1.4.241 and 1.4.243 with Claude Code, on tiny tasks; see the
  [0.5.6 validation](docs/RELEASE-0.5.6.md#validation). Codex in Orca is
  unobserved.
- **In an Orca bot**, you set up one lead bot per project by hand, from the
  [bot kit](docs/orca-bots.md). hStack ships no setup skill. The bot runs
  `hugues-mode` in its own chat, coordinates and edits no repo: every change
  goes to a worker in its own worktree, which Orca makes. It pushes and opens a
  PR only when you typed the go-ahead in the bot's own chat for that job, and it
  never merges or releases. The [Orca bot page](plugin/adapters/hosts/orca-bot.md)
  gives the mechanics and
  [ADR 0007](docs/adr/0007-an-orca-bot-uses-supervised-workers-as-transport.md)
  the reason.

  Status: released in 0.5.11; see the
  [0.5.11 validation](docs/RELEASE-0.5.11.md#validation). The page's Orca facts
  were observed on Orca 1.4.271 with a Claude Code bot and Claude Code workers; a
  few, stamped 1.4.269, were seen during the update and may come from either
  build. On 2026-11-27, on Orca 1.4.277, a proof run with a throwaway bot and repo
  observed the door, an owner-typed run to its end, a handoff run with an
  implementer and a fresh reviewer, a lost worker, and the deny file for Gmail,
  Drive and Calendar. On 2026-11-28, on Orca 1.4.281 with the released 0.5.11,
  a second run with the same bot and repo, in a new chat, observed, once each, a
  bot turn killed as its `worker_done` wake began, a handoff run that pushed
  nothing and saved its PR title and body locally, and worktrees under a custom
  base path. It also saw the worker text corrected in #172: the bot took
  `mode: structured` as no gap, and each worker listed the files it read. Its
  origin was a local bare repo, not GitHub. The kit's SOUL-first step order and
  its Never line against offering to break a Never line are defined, not yet
  observed. Gaps: a
  `worker_done` that arrives after the bot's process is already dead, the Slack
  deny entry, Codex and omp bots, Codex workers started by a bot, bot groups, a
  plain Orca chat that is not a bot, and a run with a real GitHub remote.

## What to expect

The workflows ask the agent to inspect the project, keep a task checklist, use focused workers where required, verify the result and report missing evidence. Mobile changes need checks on the affected targets. hStack does not supply Xcode, Android tooling, model access or device control.

The earlier 0.2.0 bounded trial confirmed Claude command discovery, but complete planning was blocked by isolated host startup/authentication. It did not establish full Claude/Codex workflow execution, native transcript compatibility, mobile behavior or unattended cleanup. The [0.5.0 pretest](docs/RELEASE-0.5.0.md#validation) records later Codex and
Claude Code bug-fix runs, including late checklists and the Claude permission
limits. It establishes no complete mobile journey. Read the
[0.4.0 release notes](docs/RELEASE-0.4.0.md), the [0.3.0 release notes](docs/RELEASE-0.3.0.md) and the [0.2.0 release notes](docs/RELEASE-0.2.0.md) for the evidence and limits.

## Bundled mobile guidance

Version 0.5.11 includes `swift-best-practices` and `kotlin-best-practices`.
Before source reads, the router and fresh workers read the relevant baseline in
full. Source declarations and consumer configuration select SwiftUI, UIKit,
Android Compose, KMP native-boundary and CMP wrapper references as needed.
Kotlin build scripts load no application framework guidance on their own.
Personal expert skills are optional. Existing consumer verification recipes
remain required. See [language selection](plugin/adapters/host-mobile-languages.md).

The existing review phase adds a [mobile review lens](plugin/skills/hugues-mode/references/mobile-review.md).
Runtime forensics adds [native capture and hypothesis probes](plugin/skills/hugues-mode/references/mobile-forensics.md).
Installed source contracts verify delivery and wiring. Fixtures exercise both
hosts, while a complete journey on a real consumer project remains pending in
[issue #105](https://github.com/hugues-vnsgn/hstack/issues/105).

Native build/test helpers run explicit Xcode, SwiftPM and consumer Gradle
commands, retain each attempt's full logs and native reports, and return bounded
summaries. See the [execution contract](plugin/adapters/native-execution.md).
The [0.5.1 validation](docs/RELEASE-0.5.1.md#validation) records final-source
helper observations, including failed and incomplete attempts. The
[0.5.2 validation](docs/RELEASE-0.5.2.md#validation) records the current helper
source and why no 0.5.2 fixture re-runs were made. Versions 0.5.3 to 0.5.11 do not
change the native helpers. Helper checks complement the consumer's
required native runtime proof.

## Reference and maintenance

- [Daily workflow](docs/WORKFLOW.md)
- [Maintainer reference](docs/MAINTAINER-GUIDE.md)
- [Native consolidation and migration](docs/NATIVE-CONSOLIDATION.md)
- [Source and workflow contracts](docs/CORE-RESTORATION.md)
- [Test accounting](docs/TEST-COVERAGE.md)
- [Installed planning and read-only worktree audit](plugin/adapters/host-tools.md)
- [Orca coordinator page](plugin/adapters/hosts/orca.md)
- [Orca bot page](plugin/adapters/hosts/orca-bot.md) and its [bot kit](docs/orca-bots.md)

To check a source checkout, run these commands from the hstack folder:

```sh
python3 -m unittest discover -s tests -v
./scripts/check-plugin.sh
python3 scripts/check_core.py
python3 scripts/upstream-diff.py check
python3 scripts/check_whitespace.py
```

[Source maintenance CI](.github/workflows/maintenance.yml) runs these commands on
pull requests and pushes to main. Native host and device proofs run separately.

The 0.1.0 release and its evidence remain available. Its frozen tests are historical coverage, separate from the current adapter tests. Forked under MIT. See the [upstream notice](UPSTREAM-LICENSE), the Cursor notices shipped with [deslop](plugin/skills/deslop/LICENSE), [control-cli](plugin/skills/control-cli/LICENSE) and [control-ui](plugin/skills/control-ui/LICENSE), and the [upstream pin and ledger](docs/upstream/README.md).
