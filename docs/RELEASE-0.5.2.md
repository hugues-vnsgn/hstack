# hStack 0.5.2

## What's new

Version 0.5.2 tightens native build evidence and worker handoffs for mobile development. It addresses process failures found in the 0.5.1 fixtures through [#109](https://github.com/hugues-vnsgn/hstack/issues/109) and [#110](https://github.com/hugues-vnsgn/hstack/issues/110). hStack supports Swift/iOS, Kotlin/Android, KMP and CMP development through its mobile adapter, bundled language guidance, native helpers and mobile routes. A complete journey on a real consumer project has not yet been observed on either host. That observation is the owner's BFSOne_Mobile_App run.

- Native helper use follows the command. `xcodebuild`, `swift build`, `swift test` and Gradle commands in Android, KMP or CMP projects require the helper. This includes standalone Swift packages. An unsupported command or an unresolved helper prerequisite can excuse only that command. Its raw logs and the reason belong in the evidence and final Gaps section. Worker and reviewer briefs carry absolute installed Swift/Kotlin baseline paths, read before source. Pasted mobile review guidance resolves its links too. See [#111](https://github.com/hugues-vnsgn/hstack/pull/111).
- Bounded summaries prioritize native failures, then assertions, then generic diagnostics. Every native failure gets a name and message preview before detail fills the remaining budget. Passing runs omit log-scraped diagnostics. The helper counts omitted diagnostic entries within the 8,192-byte summary limit and records the consumer's git revision and dirty state. The new tests-only `adb-instrument` entrypoint reads raw instrumentation status instead of trusting ADB exit 0. APK installation goes through the Gradle build helper first. The helper never creates or boots a device. See [#112](https://github.com/hugues-vnsgn/hstack/pull/112).
- Mobile regression workers read the test guidance, matching language baseline and named files. A stalled worker gets one fresh replacement. A second stall blocks the step, and the coordinator never writes the regression. Forked coordinator turns do not satisfy fresh-worker isolation. Complete checklist steps retain their continuation text and get evidence when reached. Host guidance maps device control and local waits, documents Codex sandbox access, and requires requested and actual worker models and effort in the reply. Both Claude agent definitions declare `model: inherit`. Live inheritance remains unobserved. See [#113](https://github.com/hugues-vnsgn/hstack/pull/113).

The pstack 0.15.25 baseline remains. The bundled Swift and Kotlin language guidance introduced in 0.5.1 still applies. Plain JVM and server Gradle projects remain outside the native helper requirement. Focused helper checks still require the consumer's affected-target proof.

## Upgrade

Update or reinstall the plugin on each host. Restart the Claude Code process after updating, then start a fresh session. A process started before the update can keep loading its old cached copy. Start a fresh Codex session too. Keep an active task on its recorded plugin copy until you reconcile its binding. The plugin remains `hstack@hstack`, Claude commands retain `/hstack:`, and the setup skill remains `setup-hstack`.

On Claude Code, refresh the configured marketplace and update the plugin:

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

For a new install, use `claude plugin install hstack@hstack`. Once the release tag exists, a session-only checkout can use the `v0.5.2` tree with `claude --plugin-dir "/absolute/path/to/hstack/plugin"`.

On Codex, refresh the configured marketplace and install its current plugin payload:

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

Check that the resolved payload reports 0.5.2. These command forms match [0.5.1's upgrade instructions](RELEASE-0.5.1.md#upgrade). On 2026-10-19, both hosts updated from 0.5.0 to 0.5.1. `claude plugin list` reported 0.5.1, and the Codex cache matched `git archive v0.5.1 plugin`. The earlier 0.4.0 to 0.5.0 update was also observed on both hosts. On 2026-10-20, these commands updated both hosts from 0.5.1 to 0.5.2. `claude plugin list` reported 0.5.2. The Codex cache matched the release plugin tree exactly. The Claude cache matched except for its runtime `.in_use` marker. If your host retains an older copy, use its supported reinstall controls and preserve the complete resource layout. Confirm native discovery before invoking `$hugues-mode` or `/hstack:hugues-mode`.

Before using `watch-pr` or `orch` from a newly installed copy, prepare its Bun dependencies once. Use a session authorized to install packages and write that copy's scripts directory. Expand `<plugin>` to the absolute root of the copy actually loaded:

```sh
cd "<plugin>/skills/hugues-mode/scripts" && bun install --frozen-lockfile && bun "<plugin>/skills/hugues-mode/scripts/watch-pr/watch-pr" --help
```

Standard roots are `~/.claude/plugins/cache/hstack/hstack/0.5.2` and `~/.codex/plugins/cache/hstack/hstack/0.5.2`. A custom loaded root takes precedence. Require exit 0 and inspect `node_modules/commander/package.json` and `node_modules/.poteto-mode-tools-install-key`. The key must equal SHA-256 of `package.json`, a NUL byte and `bun.lock`, in that order. The help call lets the bootstrap write that key. A standalone frozen install does not write it. If setup lacks authority or the directory is not writable, hold the dependent step and report the expanded command. This setup does not widen the consumer sandbox.

Codex can start with `--add-dir <evidence store> --add-dir <worktree root>` to keep evidence in its chosen store. Otherwise, request escalation for the direct command that needs access. Directory access does not establish permission to run ADB, CoreSimulator, Gradle or SwiftPM. See the [sandbox guidance](../plugin/adapters/host-workflow-tools.md#codex-sandbox).

For upgrades from 0.4.x, also follow [0.5.0's settings and plan migration](RELEASE-0.5.0.md#upgrade-from-04x). Preserve unrelated settings and evidence. Reconcile changed bindings explicitly. Do not rewrite hashes to hide unexpected drift.

## Validation

The integrated release tree collects 540 top-level unittest cases, including the driver for 50 separate frozen restoration cases. Static checks establish source and wiring contracts. Native helper observations and host fixture verdicts have the separate scopes below.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 540 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 59 skills | Plugin layout, manifests and installed payload. |
| `python3 scripts/check_core.py` | PASS | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 169 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

The prior [0.5.1 helper validation](RELEASE-0.5.1.md#validation) retains its eleven native runs and exact helper digest. Those observations remain historical evidence for that source.

The 0.5.1 fixture matrix had one planted-defect run per cell. Its [recorded results](https://github.com/hugues-vnsgn/hstack/issues/105#issuecomment-6274905838) found the reference root cause and a failing-before, passing-after regression in every cell. The verdict also checks hStack's process. These are historical fixture verdicts, not 0.5.2 re-runs or real-project support.

| Historical fixture run | Recorded verdict | Scope and limit |
|---|---|---|
| SwiftPM on Claude Code | VERIFIED, with caveats | Host package fixture. No mobile target claim. |
| SwiftPM on Codex | NOT VERIFIED | Helper never loaded. |
| Swift/iOS on Claude Code | VERIFIED, with deviations | Disposable fixture. No real-project support claim. |
| Swift/iOS on Codex | NOT VERIFIED | Coordinator wrote the regression. |
| Kotlin/Android on Claude Code | NOT VERIFIED | Helper skipped. |
| Kotlin/Android on Codex | VERIFIED, with deviations | Disposable fixture. No real-project support claim. |
| KMP on Claude Code | VERIFIED, with deviations | Disposable shared-logic fixture. |
| KMP on Codex | VERIFIED, with deviations | Disposable shared-logic fixture. |
| CMP on Claude Code | VERIFIED, with deviations | Disposable shared-UI fixture. |
| CMP on Codex | VERIFIED, with deviations | Disposable shared-UI fixture. |

The following retained observations have narrower scope. The three final-source helper attempts used SHA-256 `94fc14895b920fba2356ac627baa3d4a1b5c86211a5cab3f5a87f59e3cf3d154`, which matches the merged helper in this release. Counts are executed, failed and skipped. These observations ran through the local helper in Codex. They do not establish a complete host or mobile workflow.

| Retained observed run | Recorded result | Scope and limit |
|---|---|---|
| Claude Code update, 0.5.0 to 0.5.1, 2026-10-19 | Observed | Plugin list reported 0.5.1. Historical update only. |
| Codex update, 0.5.0 to 0.5.1, 2026-10-19 | Observed | Cache matched the tagged plugin tree. Historical update only. |
| Claude Code update, 0.5.1 to 0.5.2, 2026-10-20 | Observed | Plugin list reported 0.5.2. Cache matched the release plugin tree except for `.in_use`. |
| Codex update, 0.5.1 to 0.5.2, 2026-10-20 | Observed | Cache matched the release plugin tree exactly. |
| Codex directory-access check, 2026-10-20 | Writes succeeded | Reported launch with the worktree root added. Sandboxed writes under that root succeeded. No arbitrary-path or native-tool access claim. |
| Final-source Gradle install | Passed, `build_only`, native exit 0 | Installed app and test APKs. Test counts unknown. No connected-test claim. |
| Final-source direct instrumentation | Passed, complete, 1 / 0 / 0, native exit 0 | Explicit emulator serial on `Medium_Phone_API_36.1 -read-only -no-snapshot-save`. |
| Final-source missing-device instrumentation | Incomplete, native exit 1, helper exit 2 | Explicit nonexistent serial. Counts unknown. It cannot satisfy a failing regression. |

Retained local evidence is beside the maintainer repository under `hstack.worktrees/_notes/issue-109/release-0.5.2-evidence/`. `final-helper-receipt.json` records the helper hash and the install, instrumentation and missing-device attempts. It retains their original paths and log hashes. The owned emulator was stopped, and invocation metadata, summaries, logs and report manifests were reopened. `directory-access-observation.md` records the directory-access scope. These files are not bundled with the plugin. The committed [native captures](../tests/fixtures/native-execution/README.md) support the parsing regressions.

Earlier Claude review jobs on [#111](https://github.com/hugues-vnsgn/hstack/actions/runs/39358503366), [#112](https://github.com/hugues-vnsgn/hstack/actions/runs/39359814405) and [#113](https://github.com/hugues-vnsgn/hstack/actions/runs/39361441211) rejected the `ANTHROPIC_API_KEY` secret before a model call, with `is_error: true`, zero cost and no model usage. [#114](https://github.com/hugues-vnsgn/hstack/pull/114) switched both Claude workflows to `CLAUDE_CODE_OAUTH_TOKEN`.

The [first review on release PR #115](https://github.com/hugues-vnsgn/hstack/actions/runs/39364795054), at `e01adfe`, also failed. The OAuth input was present, but the result was `is_error: true`, `total_cost_usd: 0` and `modelUsage: {}`. Initialization named `claude-sonnet-5-5`; no model use was observed. The action hid the underlying execution error. After the token secret was regenerated, a [rerun of that review](https://github.com/hugues-vnsgn/hstack/actions/runs/39365425609) completed with `is_error: false`, 4 turns and a nonzero cost, so the earlier secret was the cause.

### Fixture re-runs

The four planned fixture re-runs (SwiftPM and Swift/iOS on Codex, Kotlin/Android and KMP on Claude Code) were not run for this release, to limit token cost. The 0.5.1 fixture verdicts above therefore remain the latest fixture evidence. Whether hosts follow the 0.5.2 rules in a live run is unobserved.

## Known gaps

- hStack supports Swift/iOS, Kotlin/Android, KMP and CMP development through its mobile adapter, bundled language guidance, native helpers and mobile routes. A complete journey on a real consumer project remains unobserved on either host. That observation is the owner's BFSOne_Mobile_App run. The planned 0.5.2 fixture re-runs were not run.
- Gradle `connected*AndroidTest` remains unobserved because `android-test-plugin-host-additional-test-output` is missing. Direct instrumentation does not establish that path. Device handling of instrumentation `-3` ignored bundles also remains unobserved.
- Claude Code `model: inherit` remains unobserved after the update. No Claude Code worker was spawned on 0.5.2 to show which model ran. Live adoption of the new regression, checklist, control, wait and escalation rules is unobserved. Source wording tests alone do not establish compliance.
- The 0.5.0 to 0.5.1 and 0.5.1 to 0.5.2 updates were observed on both hosts. Restart Claude Code after updating because an existing process can retain its older plugin cache.
- The earlier Claude review failures came from a rejected `ANTHROPIC_API_KEY`, before model use. #114 changed both workflows to `CLAUDE_CODE_OAUTH_TOKEN`. The first review of release PR #115 also failed until the token secret was regenerated. Its rerun reached a model. The watcher's match on bot login `claude` remains unconfirmed.
- Codex between-turn scheduling remains unavailable. Active-session waits do not establish a scheduler binding. [#34](https://github.com/hugues-vnsgn/hstack/issues/34) items 4 and 5, native history acquisition and managed cloud workers, remain deferred. The optional Orca adapter in [#50](https://github.com/hugues-vnsgn/hstack/issues/50) and [#96](https://github.com/hugues-vnsgn/hstack/issues/96) remain open.
- Both final 0.5.0 host runs wrote their checklists after reproduction. The accepted Claude run used headless bypassPermissions with hooks disabled. Those observations do not establish interactive completion under normal permissions, full checklist adherence or an isolated no-todo-tool fallback. Single runs do not establish repeatability.
- Codex's default read-only sandbox blocked first-time dependency installation into the plugin cache in the earlier pretest. Authorized setup enabled later helper use. Added-directory writes do not establish cache installation under those default permissions.
- Native skill creation and categorized updates, whole-map maintenance, replacement-coordinator store recovery, Origin execution and Electron control remain outside the completed release observations.
- Native report compatibility is limited to exercised formats and toolchains. Unsupported formats, ambiguous target identity and unavailable required tools remain incomplete evidence. No broad toolchain compatibility or performance improvement is claimed.
- Gradle `-b` / `--build-file` and `-c` / `--settings-file` are not rejected by the helper. These options were removed in Gradle 9. Parameterized Swift Testing cases count once per function because native xunit records them that way.
- Native nonverbose XCTest output can omit skip visibility. Use the documented `--parallel --verbose` recipe. Ambiguous XML-only results remain incomplete. Hostile descendant-process cleanup remains unobserved.
- A standalone all-disabled Swift Testing run and a Swift build with multiple compiler errors were absent from the eleven final 0.5.1 native observations. Final 0.5.1 Gradle observations exercised JVM tests, not a KMP native target. Earlier native KMP runs remain historical. This release's final-source helper observations add Android installation, direct instrumentation and a missing-device outcome. They do not fill the other native gaps.
