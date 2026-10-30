# hStack

hStack gives Claude Code, Codex and Cursor a set of workflows for investigating, changing and checking code. It adds guidance for Swift/iOS, Kotlin/Android, Kotlin Multiplatform (KMP) shared logic and Compose Multiplatform (CMP) shared UI. Your app stays in its own repository.

Version **0.5.7** adds Cursor as a third native host, so a Cursor user installs
the plugin, sees its skills and runs `/hugues-mode`, `/hugues-help` and
`/setup-hstack` in the Cursor IDE. A `.cursor-plugin/` manifest pair points at
the same `plugin/skills/` and `plugin/agents/`, so one tree serves all three
hosts. Start a run by typing
`/hstack:hugues-mode` in Claude Code or `$hugues-mode` in Codex. The release
keeps the pstack 0.15.32 baseline and the native helpers unchanged. The [0.5.7 release notes](docs/RELEASE-0.5.7.md) record
upgrade steps, checks and remaining gaps. hStack supports Swift/iOS, Kotlin/Android, KMP
and CMP development through its mobile adapter. A complete journey on a real
consumer project remains unobserved on any host. The plugin remains `hstack`. Its
commands start with `/hstack:`, and the setup skill is `setup-hstack`.
The 0.5.0 release has 57 public skills, 23 generic playbooks, two agents and four mobile playbooks.
Version 0.5.1 added two authored user-only language skills. Version 0.5.7 has 63 in total. Each skill owns one canonical `SKILL.md`.
Against 0.3.0's 50 skills, 0.4.0 merges pstack 0.15.25 and adds four user-only
skills. After 0.4.0, hStack bundles `deslop`, `control-cli` and `control-ui` from
Cursor's `cursor-team-kit`. pstack calls these skills but does not ship them.
Exact pstack source remains in a provenance archive outside
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
remove pstack first, because 55 of hStack's 63 skill names are shared with
pstack:

```sh
rm -rf "$HOME/.cursor/plugins/local/pstack"
```

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
to 0.5.5, from 0.5.5 to 0.5.6 and from 0.5.6 to 0.5.7 remains unobserved. See the [upgrade instructions](docs/RELEASE-0.5.7.md#upgrade). If
`hugues-mode` is unavailable or disabled, stop; direct-reading its body is
not an invocation fallback. The [developer guide](docs/DEVELOPER-GUIDE.md#use-codex)
explains the boundary and a first-task workflow.

## What to expect

The workflows ask the agent to inspect the project, keep a task checklist, use focused workers where required, verify the result and report missing evidence. Mobile changes need checks on the affected targets. hStack does not supply Xcode, Android tooling, model access or device control.

The earlier 0.2.0 bounded trial confirmed Claude command discovery, but complete planning was blocked by isolated host startup/authentication. It did not establish full Claude/Codex workflow execution, native transcript compatibility, mobile behavior or unattended cleanup. The [0.5.0 pretest](docs/RELEASE-0.5.0.md#validation) records later Codex and
Claude Code bug-fix runs, including late checklists and the Claude permission
limits. It establishes no complete mobile journey. Read the
[0.4.0 release notes](docs/RELEASE-0.4.0.md), the [0.3.0 release notes](docs/RELEASE-0.3.0.md) and the [0.2.0 release notes](docs/RELEASE-0.2.0.md) for the evidence and limits.

## Bundled mobile guidance

Version 0.5.7 includes `swift-best-practices` and `kotlin-best-practices`.
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
source and why no 0.5.2 fixture re-runs were made. Versions 0.5.3 to 0.5.7 do not
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

The 0.1.0 release and its evidence remain available. Its frozen tests are historical coverage, separate from the current adapter tests. Forked under MIT. See [pstack's notice](PSTACK-LICENSE), the Cursor notices shipped with [deslop](plugin/skills/deslop/LICENSE), [control-cli](plugin/skills/control-cli/LICENSE) and [control-ui](plugin/skills/control-ui/LICENSE), and the [upstream pin and ledger](docs/upstream/README.md).
