# hStack 0.5.4

## What's new

Version 0.5.4 makes `hugues-mode` user-only, as pstack's `poteto-mode` is. Start a run by typing `/hstack:hugues-mode` in Claude Code or `$hugues-mode` in Codex. A task described without it no longer starts hStack. The [#22 routing eval](hugues-mode-router-eval.md) had seen the router start unprompted on 3 of 4 task prompts. The owner chose pstack's design over that reach.

- **User-only router ([#126](https://github.com/hugues-vnsgn/hstack/pull/126)).** `hugues-mode` sets `disable-model-invocation: true`, and its Codex policy turns implicit invocation off. Its description follows `poteto-mode`'s style line. Only `setup-hstack` stays in the host's skill list. Claude Code cannot preload a user-only skill into a subagent, so `hugues-agent` reads the mode's `SKILL.md` from its parent's path, else from the installed plugins, as `poteto-agent` does. [ADR 0003](adr/0003-hugues-mode-is-user-only.md) records the decision.
- **Questions to the user (#126).** The router's question trigger no longer names `AskUserQuestion`, which subagents do not get and Codex has no observed equivalent for. It says to ask the user. A fact the agent could observe still gets a prototype instead of a question. On a product or preference call no experiment can settle, the agent interviews the user until they reach a shared understanding.
- **Full Claude model IDs ([#119](https://github.com/hugues-vnsgn/hstack/pull/119)).** `setup-hstack` writes `claude-haiku-5-5`, `claude-sonnet-5-5` and `claude-opus-5-5` instead of aliases, so a role keeps its version when an alias moves. Where Claude Code's Agent tool accepts only aliases, the alias is passed. A Fast tier (`claude-haiku-5-5` or `gpt-6-luna`) now runs the `how` explorer. Later commits retuned the default efforts and panels. Fable backs no default role, so the Frontier tier folded into Judgment.
- **control-ui server writes and logins ([#122](https://github.com/hugues-vnsgn/hstack/pull/122), [#127](https://github.com/hugues-vnsgn/hstack/pull/127)).** control-ui gets a yes before any server write. It logs in from the project's secret file without printing the values, or asks the user to log in. The rules sit in the skill's Guardrails. A read-only run against a shared backend had typed into an existing record and printed a password.
- **Editable bundled Cursor skills ([#125](https://github.com/hugues-vnsgn/hstack/pull/125)).** The checker no longer pins the bodies of `deslop`, `control-cli` and `control-ui` to their Cursor source. It still pins the source copy, the license, the receipt, the user-only flag and the host contract.
- **Skill authoring ([#123](https://github.com/hugues-vnsgn/hstack/pull/123)).** The authoring playbook's create-skill step resolves to the writing-for-agents skill plus package checks on Claude Code and Codex.

The native build and test helpers, the Bun scripts, the mobile adapter, the bundled Swift and Kotlin guidance and the pstack 0.15.25 baseline are unchanged from 0.5.3. The skill count stays at 59.

## Upgrade

Update or reinstall the plugin on each host. Restart the Claude Code process after updating, then start a fresh session. A process started before the update can keep loading its old cached copy. Start a fresh Codex session too. Keep an active task on its recorded plugin copy until you reconcile its binding. The plugin remains `hstack@hstack`, Claude commands retain `/hstack:`, and the setup skill remains `setup-hstack`.

On Claude Code, refresh the configured marketplace and update the plugin:

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

For a new install, use `claude plugin install hstack@hstack`. Once the release tag exists, a session-only checkout can use the `v0.5.4` tree with `claude --plugin-dir "/absolute/path/to/hstack/plugin"`.

On Codex, refresh the configured marketplace and install its current plugin payload:

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

Check that the resolved payload reports 0.5.4. These command forms match [0.5.3's upgrade instructions](RELEASE-0.5.3.md#upgrade). Both hosts on the maintainer machine hold 0.5.3 copies, dated 2026-10-20, that match the `v0.5.3` tag apart from installed dependencies. The update from 0.5.3 to 0.5.4 has not been observed on either host. If your host retains an older copy, use its supported reinstall controls and preserve the complete resource layout.

After updating, type `/hstack:hugues-mode` or `$hugues-mode` to start a run. A Codex worker brief names `$hugues-mode` or the mode's absolute path, because the implicit catalog entry is gone. To adopt the full model IDs and retuned defaults, rerun `/setup-hstack`. It reads an existing `.hstack/models.md` as the current choices.

Before using `watch-pr` or `orch` from a newly installed copy, prepare its Bun dependencies once. Use a session authorized to install packages and write that copy's scripts directory. Expand `<plugin>` to the absolute root of the copy actually loaded:

```sh
cd "<plugin>/skills/hugues-mode/scripts" && bun install --frozen-lockfile && bun "<plugin>/skills/hugues-mode/scripts/watch-pr/watch-pr" --help
```

Standard roots are `~/.claude/plugins/cache/hstack/hstack/0.5.4` and `~/.codex/plugins/cache/hstack/hstack/0.5.4`. A custom loaded root takes precedence. Require exit 0 and inspect `node_modules/commander/package.json` and `node_modules/.poteto-mode-tools-install-key`. The key must equal SHA-256 of `package.json`, a NUL byte and `bun.lock`, in that order. The help call lets the bootstrap write that key. A standalone frozen install does not write it. If setup lacks authority or the directory is not writable, hold the dependent step and report the expanded command. This setup does not widen the consumer sandbox. The `package.json` and `bun.lock` inputs are unchanged from 0.5.3, but each new copy needs its own install.

Codex can start with `--add-dir <evidence store> --add-dir <worktree root>` to keep evidence in its chosen store. Otherwise, request escalation for the direct command that needs access. Directory access does not establish permission to run ADB, CoreSimulator, Gradle or SwiftPM. See the [sandbox guidance](../plugin/adapters/host-workflow-tools.md#codex-sandbox).

For upgrades from 0.4.x, also follow [0.5.0's settings and plan migration](RELEASE-0.5.0.md#upgrade-from-04x). Preserve unrelated settings and evidence. Reconcile changed bindings explicitly. Do not rewrite hashes to hide unexpected drift.

## Validation

The release tree collects 540 top-level unittest cases, the same count as 0.5.3. The changes since 0.5.3 edited existing tests and added none. Static checks establish source and wiring contracts only.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 540 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 59 skills | Plugin layout, manifests and installed payload. |
| `python3 scripts/check_core.py` | PASS | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 169 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

On 2026-10-22, Claude Code 2.1.307 loaded the #126 plugin tree for one print-mode session with hooks and MCP off. Asked to list the `hstack:` skills in its Skill tool, the model answered `hstack:setup-hstack`. The same probe against `main` before #126 answered `hstack:hugues-mode` and `hstack:setup-hstack`. Typing `/hstack:hugues-mode` loaded the router. These lists are model-reported, not a host API.

The Bun scripts are unchanged, so `bun test ./watch-pr` was not rerun. The [0.5.3 validation](RELEASE-0.5.3.md#validation) and [0.5.2 validation](RELEASE-0.5.2.md#validation) still describe the watcher and the native helpers. No fixture run was made for 0.5.4.

## Known gaps

- Codex with implicit invocation off for `hugues-mode` is unobserved, including `$hugues-mode` under the new policy.
- No live `hugues-agent` has read the mode by path, and no real run has used the interview wording.
- No host run has exercised the control-ui server-write and login rules.
- No session has run with the full model IDs that `setup-hstack` now writes.
- The update from 0.5.3 to 0.5.4 is unobserved on both hosts.
- Every [0.5.3 known gap](RELEASE-0.5.3.md#known-gaps) still applies. A complete journey on a real consumer project remains unobserved on either host.
