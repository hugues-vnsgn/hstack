# hStack 0.5.6

## What's new

Version 0.5.6 lets a coordinator in an Orca pane run hStack workers in other Orca panes. It reshapes the shared host adapter into the tables of pstack's own Claude Code adapter, adds a hosts index that a session reads only inside an ADE, and ships hStack's first plugin hook.

- **Host adapter in pstack's shape ([#142](https://github.com/hugues-vnsgn/hstack/pull/142)).** `plugin/adapters/host.md` and `plugin/adapters/host-workers.md` now use the tables of pstack's `docs/harness/claude-code.md` at pin `e73df471`. A drift test fails when upstream adds a row to that file. [ADR 0004](adr/0004-adapters-for-ades-and-agents.md) sets the rules for an ADE or agent adapter, and [plugin/adapters/hosts/README.md](../plugin/adapters/hosts/README.md) is the index of those adapters.
- **Session-start hook (#142).** `plugin/hooks/hooks.json` runs `plugin/hooks/host-detect.sh` when a Claude Code session starts. If `ORCA_TERMINAL_HANDLE`, `ORCA_PANE_KEY` or `ORCA_TAB_ID` is set, the hook tells the session to read the hosts index. Otherwise it prints nothing. Codex and omp load no plugin hook, so they keep the written check in `host-workers.md`.
- **Orca page ([#143](https://github.com/hugues-vnsgn/hstack/pull/143)).** [plugin/adapters/hosts/orca.md](../plugin/adapters/hosts/orca.md) tells a coordinator in an Orca pane how to start, send to, read, wait for and close worker panes. It also says how to record each worker and to treat a pane that closed before DONE as a lost worker. The page refuses Orca's own Runs, Tasks, Dispatches and `worker_done`. hStack still owns dispatch, completion and verification. A worker runs with `--permission-mode bypassPermissions` only when the task states that the owner approved it. Otherwise it runs in the user's default mode.
- **Counts.** The tree collects 553 test cases, up from 540 at 0.5.5. The skill count stays at 63. The size cap on the hosts index rose from 1,500 to 1,750 bytes, with the owner's approval.

The native build and test helpers, the mobile adapters, the bundled Swift and Kotlin guidance, the agents, and the Bun dependency inputs (`package.json`, `bun.lock`) are unchanged from 0.5.5. The pstack baseline stays at 0.15.32.

## Upgrade

Update or reinstall the plugin on each host. Restart the Claude Code process after updating, then start a fresh session. A process started before the update can keep loading its old cached copy. Start a fresh Codex session too. The plugin remains `hstack@hstack`, Claude commands keep `/hstack:`, and the setup skill remains `setup-hstack`.

On Claude Code, refresh the configured marketplace and update the plugin:

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

For a new install, use `claude plugin install hstack@hstack`. Once the release tag exists, a session-only checkout can use the `v0.5.6` tree with `claude --plugin-dir "/absolute/path/to/hstack/plugin"`.

On Codex, refresh the configured marketplace and install its current plugin payload:

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

Check that the resolved payload reports 0.5.6. The marketplace follows the default branch. On the maintainer machine, the Codex cache under the 0.5.5 label already held #142's content before this release, while the Claude Code cache matched `v0.5.5`. The update from 0.5.5 to 0.5.6 has not been observed on either host.

Each new copy needs its Bun dependencies once before `watch-pr` or `orch` runs. Follow [0.5.4's setup command](RELEASE-0.5.4.md#upgrade) with `<plugin>` set to the 0.5.6 copy. The `package.json` and `bun.lock` inputs are unchanged from 0.5.5.

For upgrades from 0.4.x, also follow [0.5.0's settings and plan migration](RELEASE-0.5.0.md#upgrade-from-04x).

## Validation

Static checks establish source and wiring contracts only. They ran at the release head.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 553 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 63 skills | Plugin layout, manifests and installed payload. |
| `python3 scripts/check_core.py` | PASS, 200 archive files | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 200 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

`claude plugin validate --strict` passes on `plugin` and on the marketplace.

The maintainer's runs for #142 and #143 observed the following. The evidence stays in the maintainer's private store.

- The hook fired in Claude Code 2.1.311 and named the hosts index of the loaded plugin. A plain session, outside Orca, got no added context.
- On Orca CLI 1.4.241 and 1.4.243 with Claude Code 2.1.312, coordinators in Orca panes read the hosts index and then `orca.md` before their first dispatch.
- Coordinators drove runs with one worker pane and with two, and closed every pane they opened. Five minutes after DONE, 0 worker processes were alive, compared with 2 at the parent commit.
- A coordinator waited past a timeout and then collected DONE. When someone closed a worker pane from outside, the coordinator reported a lost worker.
- Coordinators refused Orca's task system, and passed `--plugin-dir` and the requested model to their workers.
- A coordinator started an owner-approved worker in bypass mode, and without approval started a worker in the user's default mode.

The verdict comments on [#143](https://github.com/hugues-vnsgn/hstack/pull/143) record the Orca runs.

## Known gaps

- Codex in Orca, omp, and T3 Code are unobserved. This release has no T3 Code or omp page.
- `orca agent launch` with `--model`, `--effort`, `--prompt` or `--retry-launch` is unobserved, and so is the send-timeout path.
- The Orca tests used tiny tasks. For budget, the owner cut fixture builds, simulators and emulators. So no one checked whether the workers' fixes pass the regression diffs of the mobile fixtures.
- A coordinator in Claude Code's auto mode cannot start a bypass worker unless the owner's approval is stated. Claude Code's classifier denies it.
- The update from 0.5.5 to 0.5.6 is unobserved on both hosts.
- Upstream pstack has moved to 0.15.34. hStack stays on 0.15.32 for this release.
- Every [0.5.5 known gap](RELEASE-0.5.5.md#known-gaps) still applies.
