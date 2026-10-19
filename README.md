# hStack

hStack gives Claude Code and Codex a set of workflows for investigating, changing and checking code. It adds guidance for Swift/iOS, Kotlin/Android, Kotlin Multiplatform (KMP) shared logic and Compose Multiplatform (CMP) shared UI. Your app stays in its own repository.

Version **0.5.1** adds bundled Swift and Kotlin guidance, a mobile review lens,
native forensics and bounded Xcode, SwiftPM and Gradle helpers. It keeps the
pstack 0.15.25 workflow baseline. The [0.5.1 release notes](docs/RELEASE-0.5.1.md)
record upgrade steps, observed helper runs and remaining gaps. Complete mobile
journeys on Claude Code and Codex remain unobserved. The plugin remains `hstack`. Its
commands start with `/hstack:`, and the setup skill is `setup-hstack`.
The 0.5.0 release has 57 public skills, 23 generic playbooks, two agents and four mobile playbooks.
Version 0.5.1 adds two authored user-only language skills for 59 total. Each skill owns one canonical `SKILL.md`.
Against 0.3.0's 50 skills, 0.4.0 merges pstack 0.15.25 and adds four user-only
skills. After 0.4.0, hStack bundles `deslop`, `control-cli` and `control-ui` from
Cursor's `cursor-team-kit`. pstack calls these skills but does not ship them.
Exact pstack source remains in a provenance archive outside
runtime discovery. Only `hugues-mode` and `setup-hstack` appear in the host's
skill list; the router reads the other skills as files. The published 0.1.0, 0.2.0 and 0.3.0 releases and
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

## Start with Codex

Use a supported native discovery/invocation route and confirm that `hugues-mode`
appears before using `$hugues-mode`. The 0.5.0 pretest exercised an installed
Codex copy. The 0.4.0 to 0.5.0 update was later observed on both hosts. Updating
to 0.5.1 remains unobserved. See the [upgrade instructions](docs/RELEASE-0.5.1.md#upgrade). If
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

Version 0.5.1 includes `swift-best-practices` and `kotlin-best-practices`.
Before source reads, the router and fresh workers read the relevant baseline in
full. Source declarations and consumer configuration select SwiftUI, UIKit,
Android Compose, KMP native-boundary and CMP wrapper references as needed.
Kotlin build scripts load no application framework guidance on their own.
Personal expert skills are optional. Existing consumer verification recipes
remain required. See [language selection](plugin/adapters/host-mobile-languages.md).

The existing review phase adds a [mobile review lens](plugin/skills/hugues-mode/references/mobile-review.md).
Runtime forensics adds [native capture and hypothesis probes](plugin/skills/hugues-mode/references/mobile-forensics.md).
Installed source contracts verify delivery and wiring. Fresh native host and
mobile journeys for this upgrade remain a later phase of [issue #105](https://github.com/hugues-vnsgn/hstack/issues/105).

Native build/test helpers run explicit Xcode, SwiftPM and consumer Gradle
commands, retain each attempt's full logs and native reports, and return bounded
summaries. See the [execution contract](plugin/adapters/native-execution.md).
The [0.5.1 validation](docs/RELEASE-0.5.1.md#validation) records final-source
helper observations, including failed and incomplete attempts. Helper checks
complement the consumer's required native runtime proof.

## Reference and maintenance

- [Daily workflow](docs/WORKFLOW.md)
- [Maintainer reference](docs/MAINTAINER-GUIDE.md)
- [Native consolidation and migration](docs/NATIVE-CONSOLIDATION.md)
- [Source and workflow contracts](docs/CORE-RESTORATION.md)
- [Test accounting](docs/TEST-COVERAGE.md)
- [Installed planning and read-only worktree audit](plugin/adapters/host-tools.md)

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
