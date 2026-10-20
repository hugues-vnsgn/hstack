# hStack 0.5.3

## What's new

Version 0.5.3 lets the PR watcher wait for status contexts that a consumer's rules require. Local CI can take time to post its first status. Before this release, a PR head with no checks yet used up the watcher's query-error retries, and unrelated passing checks could hide a required status that had not posted.

- `watch-pr` accepts a repeatable `--require-context <name-or-prefix>` flag. A value matches a check by exact name. A value that ends in `/` matches every check whose name starts with it. An empty value is rejected.
- A required context that has not posted on the PR head reads as a pending check named after the context. The watcher waits instead of exhausting the query-error budget. Single, stack and queued modes all report it. JSON output gives it `reportedState` `MISSING`, and `--pretty` output marks it `(missing required context)`.
- The babysit playbook tells agents to pass each required context from the consumer's rules. The shipping playbook passes the same flags to the queued watcher.
- Without the flag, the watcher behaves as it did in 0.5.2.

See [#117](https://github.com/hugues-vnsgn/hstack/pull/117). The native build and test helpers, the mobile adapter, the bundled Swift and Kotlin guidance and the pstack 0.15.25 baseline are unchanged from 0.5.2. The skill count stays at 59.

## Upgrade

Update or reinstall the plugin on each host. Restart the Claude Code process after updating, then start a fresh session. A process started before the update can keep loading its old cached copy. Start a fresh Codex session too. Keep an active task on its recorded plugin copy until you reconcile its binding. The plugin remains `hstack@hstack`, Claude commands retain `/hstack:`, and the setup skill remains `setup-hstack`.

On Claude Code, refresh the configured marketplace and update the plugin:

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

For a new install, use `claude plugin install hstack@hstack`. Once the release tag exists, a session-only checkout can use the `v0.5.3` tree with `claude --plugin-dir "/absolute/path/to/hstack/plugin"`.

On Codex, refresh the configured marketplace and install its current plugin payload:

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

Check that the resolved payload reports 0.5.3. These command forms match [0.5.2's upgrade instructions](RELEASE-0.5.2.md#upgrade). On 2026-10-20, they updated both hosts from 0.5.1 to 0.5.2. The update from 0.5.2 to 0.5.3 has not been observed on either host. If your host retains an older copy, use its supported reinstall controls and preserve the complete resource layout. Confirm native discovery before invoking `$hugues-mode` or `/hstack:hugues-mode`.

Before using `watch-pr` or `orch` from a newly installed copy, prepare its Bun dependencies once. Use a session authorized to install packages and write that copy's scripts directory. Expand `<plugin>` to the absolute root of the copy actually loaded:

```sh
cd "<plugin>/skills/hugues-mode/scripts" && bun install --frozen-lockfile && bun "<plugin>/skills/hugues-mode/scripts/watch-pr/watch-pr" --help
```

Standard roots are `~/.claude/plugins/cache/hstack/hstack/0.5.3` and `~/.codex/plugins/cache/hstack/hstack/0.5.3`. A custom loaded root takes precedence. Require exit 0 and inspect `node_modules/commander/package.json` and `node_modules/.poteto-mode-tools-install-key`. The key must equal SHA-256 of `package.json`, a NUL byte and `bun.lock`, in that order. The help call lets the bootstrap write that key. A standalone frozen install does not write it. If setup lacks authority or the directory is not writable, hold the dependent step and report the expanded command. This setup does not widen the consumer sandbox. The `package.json` and `bun.lock` inputs are unchanged from 0.5.2, but each new copy needs its own install.

Codex can start with `--add-dir <evidence store> --add-dir <worktree root>` to keep evidence in its chosen store. Otherwise, request escalation for the direct command that needs access. Directory access does not establish permission to run ADB, CoreSimulator, Gradle or SwiftPM. See the [sandbox guidance](../plugin/adapters/host-workflow-tools.md#codex-sandbox).

For upgrades from 0.4.x, also follow [0.5.0's settings and plan migration](RELEASE-0.5.0.md#upgrade-from-04x). Preserve unrelated settings and evidence. Reconcile changed bindings explicitly. Do not rewrite hashes to hide unexpected drift.

## Validation

The release tree collects 540 top-level unittest cases, the same count as 0.5.2, because #117 added no Python tests. Static checks establish source and wiring contracts only.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 540 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 59 skills | Plugin layout, manifests and installed payload. |
| `python3 scripts/check_core.py` | PASS | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 169 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

`bun test ./watch-pr` passed all 65 cases with Bun 1.3.14 on the release tree. The run used a scratch copy of the scripts directory outside the repository and `bun install --frozen-lockfile`. Nine of these cases came with #117. They cover argument validation, missing contexts, prefix matching and polling in single, stack and queued modes.

Before #117 merged, a live watcher probe on [PHQUY/BFSOne_Mobile_App#142](https://github.com/PHQUY/BFSOne_Mobile_App/pull/142) returned a terminal query-error verdict for a head with zero checks. Statuses posted later read as pending, failing and clean. That probe ran without `--require-context`. No live PR has run the watcher with the new flag.

The [0.5.2 validation](RELEASE-0.5.2.md#validation) keeps its native helper observations and historical fixture verdicts. They still describe the native helpers, which 0.5.3 does not change. No fixture or host run was made for 0.5.3.

## Known gaps

- No live PR has run `watch-pr --require-context`. Bun tests with fake GitHub readers are its only coverage.
- A misspelled context name never matches a posted check. The watcher waits until it times out or the caller stops it.
- The watcher does not discover required contexts from branch protection or rulesets. The caller names them.
- The update from 0.5.2 to 0.5.3 is unobserved on both hosts.
- Every [0.5.2 known gap](RELEASE-0.5.2.md#known-gaps) still applies. A complete journey on a real consumer project remains unobserved on either host.
