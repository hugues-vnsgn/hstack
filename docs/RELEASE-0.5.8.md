# hStack 0.5.8

## What's new

Version 0.5.8 moves the pstack pin from 0.15.32 to 0.15.36. Upstream changed 25
files, added 406 and removed 33, and the ledger grew to 573 rows. The skill count
stays at 63. The native build and test helpers, the mobile adapters, the bundled
Swift and Kotlin guidance and the agents are unchanged.

- **Orchestrate is agentic.** The coordinator keeps its program state with its own
  tools and runs no script. The `orch` helper and its tests are gone, so
  Orchestrate needs no Bun setup. Program state lives in the Project store under
  `orchestrate/<project-slug>/`, and its `notes.md` tracker lives under the agent
  store. The [workflow tools adapter](../plugin/adapters/host-workflow-tools.md)
  maps both onto the agent store.
- **interrogate keeps only the findings a run proves.** Adversaries try to break
  the change, and only a finding that a rerun proves survives. Upstream's four
  reference files are deleted. hStack keeps its host contract, its
  `.hstack/models.md` line, and the Swift and Kotlin baseline paths in every
  adversary brief.
- **statechart ships a TypeScript compiler.** Upstream's compiler replaces the
  Node scripts, and it comes with its test corpus. The suite was not run for this
  release.
- **The router takes two upstream rules.** The first message restates the goal,
  and Autopilot-stack's trigger reads "autopilot, don't merge".
- **The arena judge changes.** The cross-judge is never the parent's model, and
  it is skipped when no pool entry differs from the parent model. With no
  `.hstack/models.md` the pool default is `inherit-parent max`, so the judge is
  skipped and arena says so. At 0.5.7 the judge ran on the parent model.

The upstream re-pin also changed the ledger's accounting. Retired rows keep their
last decision with a `removed_at_revision` marker, and the changed and added
rows carry the release target `unreleased-pstack-0.15.36` until a release ships
them. The [upstream sync notes](upstream/README.md#pstack-01536-merge) record the
procedure and the archive.

## Upgrade

Update or reinstall the plugin on each host. Restart the Claude Code process
after updating, then start a fresh session. A process started before the update
can keep loading its old cached copy. Start a fresh Codex session too. The
plugin remains `hstack@hstack`, Claude commands keep `/hstack:`, and the setup
skill remains `setup-hstack`.

On Claude Code, refresh the configured marketplace and update the plugin:

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

For a new install, use `claude plugin install hstack@hstack`. Once the release
tag exists, a session-only checkout can use the `v0.5.8` tree with
`claude --plugin-dir "/absolute/path/to/hstack/plugin"`.

On Codex, refresh the configured marketplace and install its current plugin
payload:

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

Check that the resolved payload reports 0.5.8. The marketplace follows the
default branch. The update from 0.5.7 to 0.5.8 was observed on Claude Code and
in Cursor, in the release lanes recorded below.

### Bun dependencies

Every copy needs its Bun dependencies again before `watch-pr` runs. The
`package.json` in `plugin/skills/hugues-mode/scripts/` changed, because upstream
dropped the `orch` test from its `test` script. The install key is the SHA-256
of `package.json`, a NUL byte and `bun.lock`, so the changed `package.json`
changes the key, and a copy that was installed at 0.5.7 holds a stale key. The
0.5.7 sentence "the `package.json` and `bun.lock` inputs are unchanged" does not
carry over. The `bun.lock` file itself is byte-identical to the 0.5.7 one.

Run the install once per copy. Follow [0.5.4's setup command](RELEASE-0.5.4.md#upgrade)
with `<plugin>` set to the 0.5.8 copy.

```sh
cd "<plugin>/skills/hugues-mode/scripts" && bun install --frozen-lockfile && bun "<plugin>/skills/hugues-mode/scripts/watch-pr/watch-pr" --help
```

The new `plugin/skills/statechart/scripts/package.json` has no lockfile, so its
`fast-check` dependency has no reproducible install. That is a known gap.

For upgrades from 0.4.x, also follow [0.5.0's settings and plan migration](RELEASE-0.5.0.md#upgrade-from-04x).

### Installing in Cursor

Pick exactly one route. **Route A**, you already use hStack in Claude Code:
install nothing in Cursor, and Cursor loads hStack from Claude Code's install.
**Route B**, you do not use Claude Code: hold a copy of the plugin tree at
`~/.cursor/plugins/local/hstack`.

```sh
src="/absolute/path/to/hstack/plugin"
dst="$HOME/.cursor/plugins/local/hstack"
rm -rf "$dst"
mkdir -p "$dst"
cp -R "$src"/. "$dst"/
```

Copy rather than symlink. Cursor's own documentation states that a symlink in
that folder loads only when its target resolves inside that folder, and that
Cursor skips a symlink pointing outside it. This repository is outside it, so a
copy is the route that cannot break on that rule. The rule is from Cursor's
documentation, not observed in the IDE.

One source only. Cursor loads the Claude plugin cache as well as
`~/.cursor/plugins/local/`, and it de-duplicates within one plugin rather than
across plugins, so two sources register every shared skill twice.

## Validation

Static checks establish source and wiring contracts only. They ran at the release
head.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 584 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 63 skills | Plugin layout, manifests and installed payload. |
| `python3 scripts/check_core.py` | PASS, 573 archive files | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 573 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

`claude plugin validate --strict` passes on `plugin` and on the marketplace.

### The release lanes, observed

Four lanes ran in Cursor on 2026-11-01 against the installed 0.5.8 copy. The
lane sheet is at `~/hstack-evidence/2026-10-31-release-0.5.8/lanes.md` and the
transcripts and logs stay in the maintainer's private store.

- **The install.** Cursor loaded hStack from Claude Code's install at the
  `0.5.8` cache path, once, with no local copy. The plugin log records
  `loadClaudePlugin hstack@hstack loaded` and
  `loadUserLocalPlugins completed in 5.0ms (0 plugins loaded)`, with no
  `loadUserLocalPlugin hstack` line. The resolved install is
  `~/.claude/plugins/cache/hstack/hstack/0.5.8`, and the installed record's
  `gitCommitSha` is the merge commit `177628b`. The copy holds 63 skills.
- **The release notes.** `/hugues-help What changed in Orchestrate and
  interrogate in this version?` read the host contract, the Cursor page and
  both skills from the 0.5.8 cache path, and reported the `orch` helper's
  removal, interrogate's proof-gated findings, and the deleted upstream
  reference files.
- **A bug fix, test first.** In a scratch repository holding one Python
  function with an off-by-one bound and a failing unittest, a `/hugues-mode`
  run routed to the bug-fix playbook, reproduced the failure with two of three
  tests red, established the cause by probing the function across
  `n = 0, 1, 2, 3, 5, 10`, delegated the fix to one `hugues-agent`, and
  committed it on the current branch without pushing. The failing test landed
  in `1fc6154` and the fix in `9e2309a`, and the coordinator reran the suite
  independently: 3 of 3 pass.
- **An adversarial review.** `/interrogate the last commit` ran three
  adversaries in separate worktrees. The coordinator reran every claimed
  finding rather than trusting the reports, and kept two: the bound is computed
  as `n + 1` in the caller's own type, so the function accepts strictly less
  than `range()` did, and the committed suite pins the contract at `n = 0, 1`
  and `5` only. Both are recorded in the private store. Neither was applied,
  because interrogate reports findings and the scratch repository exists to
  prove the release.

## Known gaps

- **Issue [#150](https://github.com/hugues-vnsgn/hstack/issues/150)** is open and
  unfixed in this release.
- **Issue [#151](https://github.com/hugues-vnsgn/hstack/issues/151)** is open and
  unfixed in this release.
- **Issue [#152](https://github.com/hugues-vnsgn/hstack/issues/152)** is open and
  unfixed in this release.
- The statechart test suite was not run. The compiler and its corpus arrive with
  the 0.15.36 re-pin.
- No Codex session ran. The Codex install was updated through the CLI only, with
  no model call.
- The update from 0.5.7 to 0.5.8 was observed on Claude Code and in Cursor, in
  the release lanes recorded above. No Codex session ran, so the Codex side of
  the update is unobserved.
- The `plugin/skills/statechart/scripts/package.json` dependency set has no
  lockfile, so its install is not reproducible.
- Cursor, in the IDE. Stock Cursor is unobserved, and so is the free plan
  without the third-party auth extension. Every observation comes from Cursor
  3.27.22 with that extension.
- Cursor, in the IDE. A read-only Explore subagent is not observed, and no run
  confirmed that a Cursor plugin subagent leaves the working tree clean.
- Cursor, in the IDE. The paid-feature skip line is not observed. The Swift skill
  loading on a Swift task is not observed. `recall` finding an earlier chat in
  Cursor's transcripts is not observed.
- Cursor, in the IDE. Route A, where Cursor loads hStack from Claude Code's
  install, is now observed on the released plugin, with hStack on in Claude
  Code and no local copy. The plugin log records one source and no
  `loadUserLocalPlugin hstack` line.
- Cursor, in the IDE. The Cursor CLI, Cloud Agents, the Cursor SDK and T3 Code's
  Cursor provider are unsupported. A step that needs a paid Cursor plan keeps the
  skip line.
- Cursor, in the IDE. The GitHub-marketplace install route is unobserved. Cursor
  inside Orca or T3 Code is not covered.
- Cursor, in the IDE. A Cursor plugin agent cannot run in the background. The flag
  is dropped by Cursor's plugin-agent conversion, so `hugues-agent` runs in the
  foreground there. This is a written gap, not a field.
- The arena cross-judge is skipped without a `.hstack/models.md` that names a pool
  entry other than the parent model. The pool default is `inherit-parent max`.
- Codex in Orca, omp, and T3 Code are unobserved.
- Every [0.5.7 known gap](RELEASE-0.5.7.md#known-gaps) still applies.
