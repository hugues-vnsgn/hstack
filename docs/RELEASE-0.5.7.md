# hStack 0.5.7

## What's new

Version 0.5.7 makes Cursor a third native host, beside Claude Code and Codex. A Cursor user installs the plugin, sees its skills, and runs `/hugues-mode`, `/hugues-help` and `/setup-hstack` in the Cursor IDE. One tree serves all three hosts.

- **Cursor manifests.** A `.cursor-plugin/` manifest pair points at the existing `plugin/skills/` and `plugin/agents/`, with a repository-root `.cursor-plugin/marketplace.json` for the marketplace route. There is no generated tree and no copied body. `scripts/check_plugin.py` validates both Cursor manifests and holds the plugin identity across all four: name, version, description, author and license must agree.
- **Cursor page ([#146](https://github.com/hugues-vnsgn/hstack/pull/146)).** [plugin/adapters/hosts/cursor.md](../plugin/adapters/hosts/cursor.md) holds the Cursor mechanics: how a Cursor session detects itself, where its transcripts live, that a plugin agent runs in the foreground, which tools it may use, and which skip line a paid feature prints. The always-loaded adapters keep one door sentence pointing a Cursor session at that page.
- **Cursor transcripts.** The activity reader reads Cursor's `{"role", "message"}` envelope, its `text` and `tool_use` blocks and its `turn_ended` marker, and treats any other shape as unreviewed and holds coverage. The recall skill states the slug rules Cursor actually uses, because Cursor ships more than one way to compute one.
- **Model setup in Cursor.** `plugin/skills/setup-hstack/references/cursor-models.md` tells a Cursor session to detect the model ids from the agent tool's own schema in the session, and to write the Claude and Codex alternatives after them, so one `.hstack/models.md` still serves every host.
- **Identity.** The identity line, the glossary, the README, both guides and the support table name three hosts. Claude Code and Codex keep their behaviour: no edit in this release changes what those hosts load or do.

Three lanes ran by hand in Cursor 3.27.22 with a third-party auth extension, on the Auto model, against the local copy at route B. `setup-hstack` wrote `.hstack/models.md`. A `/hugues-mode` session routed to `bug-fix` and ran one foreground `hugues-agent` delegate that fixed and committed a typo. The install showed 63 hStack skills with no duplicate names, from the local copy alone.

Two claims were retired by those runs. The Cursor agent tool does expose a model id and has no effort parameter, so the model roles reference no longer says the detected set is empty. And Cursor's shell wrapper adds a `Co-authored-by` trailer to every `git commit`, which the Cursor page records without teaching agents to bypass hooks.

- **Counts.** The tree collects 583 test cases, up from 553 at 0.5.6. The skill count stays at 63. The always-loaded router read set grows by 88 bytes over 0.5.6, all of it in the host adapter: an 80-byte door sentence that points a Cursor session at its page and an 8-byte title that names the third host.

The native build and test helpers, the mobile adapters, the bundled Swift and Kotlin guidance, the agents, and the Bun dependency inputs (`package.json`, `bun.lock`) are unchanged from 0.5.6. The pstack baseline stays at 0.15.32.

## Upgrade

Update or reinstall the plugin on each host. Restart the Claude Code process after updating, then start a fresh session. A process started before the update can keep loading its old cached copy. Start a fresh Codex session too. The plugin remains `hstack@hstack`, Claude commands keep `/hstack:`, and the setup skill remains `setup-hstack`.

On Claude Code, refresh the configured marketplace and update the plugin:

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

For a new install, use `claude plugin install hstack@hstack`. Once the release tag exists, a session-only checkout can use the `v0.5.7` tree with `claude --plugin-dir "/absolute/path/to/hstack/plugin"`.

On Codex, refresh the configured marketplace and install its current plugin payload:

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

Check that the resolved payload reports 0.5.7. The marketplace follows the default branch. On the maintainer machine, the Claude Code cache matched `v0.5.6` before this release and the Cursor local copy held the PR head. The updates from 0.5.6 to 0.5.7 have not been observed on any host.

Each new copy needs its Bun dependencies once before `watch-pr` or `orch` runs. Follow [0.5.4's setup command](RELEASE-0.5.4.md#upgrade) with `<plugin>` set to the 0.5.7 copy. The `package.json` and `bun.lock` inputs are unchanged from 0.5.6.

For upgrades from 0.4.x, also follow [0.5.0's settings and plan migration](RELEASE-0.5.0.md#upgrade-from-04x).

### Installing in Cursor

Pick exactly one route. **Route A**, you already use hStack in Claude Code: install nothing in Cursor, and Cursor loads hStack from Claude Code's install. **Route B**, you do not use Claude Code: hold a copy of the plugin tree at `~/.cursor/plugins/local/hstack`.

```sh
src="/absolute/path/to/hstack/plugin"
dst="$HOME/.cursor/plugins/local/hstack"
rm -rf "$dst"
mkdir -p "$dst"
cp -R "$src"/. "$dst"/
```

Copy rather than symlink. Cursor's own documentation states that a symlink in that folder loads only when its target resolves inside that folder, and that Cursor skips a symlink pointing outside it. This repository is outside it, so a copy is the route that cannot break on that rule. The rule is from Cursor's documentation, not observed in the IDE.

One source only. Cursor loads the Claude plugin cache as well as `~/.cursor/plugins/local/`, and it de-duplicates within one plugin rather than across plugins, so two sources register every shared skill name twice.

## Validation

Static checks establish source and wiring contracts only. They ran at the release head.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 583 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 63 skills | Plugin layout, manifests and installed payload. |
| `python3 scripts/check_core.py` | PASS, 200 archive files | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 200 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

`claude plugin validate --strict` passes on `plugin` and on the marketplace.

The maintainer's runs for #146 observed the following. The evidence stays in the maintainer's private store.

- In Cursor 3.27.22 with a third-party auth extension, on the Auto model, the install showed 63 hStack skills with no duplicate names, with hStack listed once, from the local copy.
- `/hugues-help` read the host contract, the mobile adapter and the Cursor page, and its answer named Claude Code, Codex and Cursor.
- `/hugues-mode` read the Cursor page, routed to the `bug-fix` playbook, and dispatched one `hugues-agent` delegate. The delegate ran in the foreground and reported back, and the parent verified its work against the committed file rather than the delegate's report.
- `/setup-hstack` read the setup skill and the Cursor model roles, asked for a reasoning budget and a model per role, and wrote `.hstack/models.md`.
- The Cursor agent tool's own schema listed one real model id plus `inherit`, and no effort parameter.

## Known gaps

- **Cursor, in the IDE.** Stock Cursor is unobserved, and so is the free plan without the third-party auth extension. Every observation above comes from Cursor 3.27.22 with that extension.
- **Cursor, in the IDE.** A read-only Explore subagent is not observed, and no run confirmed that a Cursor plugin subagent leaves the working tree clean.
- **Cursor, in the IDE.** The paid-feature skip line is not observed. The Swift skill loading on a Swift task is not observed. `recall` finding an earlier chat in Cursor's transcripts is not observed.
- **Cursor, in the IDE.** Route A, where Cursor loads hStack from Claude Code's install, is expected, not proven. It is checked at the end, on the released plugin, with hStack on in Claude Code and no local copy.
- **Cursor, in the IDE.** The Cursor CLI, Cloud Agents, the Cursor SDK and T3 Code's Cursor provider are unsupported. A step that needs a paid Cursor plan keeps the skip line.
- **Cursor, in the IDE.** The GitHub-marketplace install route is unobserved. Cursor inside Orca or T3 Code is not covered.
- **Cursor, in the IDE.** A Cursor plugin agent cannot run in the background. The flag is dropped by Cursor's plugin-agent conversion, so `hugues-agent` runs in the foreground there. This is a written gap, not a field.
- The update from 0.5.6 to 0.5.7 is unobserved on any host.
- Codex in Orca, omp, and T3 Code are unobserved.
- Upstream pstack has moved to 0.15.34. hStack stays on 0.15.32 for this release.
- Every [0.5.6 known gap](RELEASE-0.5.6.md#known-gaps) still applies.
