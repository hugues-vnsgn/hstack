# hStack 0.5.1

## What's new

Version 0.5.1 adds bundled Swift and Kotlin guidance and native build/test helpers for mobile development. These additions implement part of [#105](https://github.com/hugues-vnsgn/hstack/issues/105). The complete Claude Code and Codex mobile journeys remain unobserved.

- `swift-best-practices` covers API design, ownership, actor isolation, cancellation and testability. It checks the consumer's language mode and concurrency settings. SwiftUI and UIKit references apply when the project uses those frameworks.
- `kotlin-best-practices` covers nullability, immutable exposed state, structured concurrency and deterministic tests. Source and configuration select Android Compose, KMP native-boundary and CMP wrapper references. A Kotlin build script alone does not select application guidance. Both language skills are bundled user-only references, so the baseline needs no personal expert-skill installation. See [#106](https://github.com/hugues-vnsgn/hstack/pull/106).
- The existing review phase gains a mobile review lens for lifecycle restoration, cancellation, main-thread work, resource release, offline recovery, accessibility and text scaling. Native forensics guidance selects capture tools and hypothesis probes for the runtime under investigation. These are authored procedures. They do not establish completed mobile journeys. See [#106](https://github.com/hugues-vnsgn/hstack/pull/106).
- Three helper entrypoints run explicit `xcodebuild`, SwiftPM and consumer Gradle wrapper commands. Each attempt retains its command metadata, full output and native reports. JSON feedback is bounded to 8,192 UTF-8 bytes, including its newline. It separates command status, report interpretation and test outcome, with artifact pointers for omitted detail. Unknown counts, zero tests, skipped tests and missing or wrong-target reports stay visible. Consumer recipes still choose the project, target and supported filters. See [#107](https://github.com/hugues-vnsgn/hstack/pull/107).

The pstack 0.15.25 baseline, action router, native invocation controls and ten-lane policy remain in place. Focused helper checks still require final proof on the affected native targets.

## Upgrade

Update or reinstall the plugin on each host. Restart the Claude Code process after updating, then start a fresh session. A process started before the update can continue loading the old cached version while its directory remains on disk. Start a fresh Codex session too. Keep an active task on its recorded plugin copy until you reconcile its binding. The plugin remains `hstack@hstack`, Claude commands retain `/hstack:`, and the setup skill remains `setup-hstack`.

On Claude Code, refresh the configured marketplace and update the plugin:

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

For a new install from that marketplace, use `claude plugin install hstack@hstack`. Once the release tag exists, a session-only checkout can use the `v0.5.1` tree with `claude --plugin-dir "/absolute/path/to/hstack/plugin"`.

On Codex, refresh the configured marketplace, then install its current plugin payload:

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

Check that the resolved payload reports 0.5.1. These command forms are carried forward from [0.5.0](RELEASE-0.5.0.md#upgrade-from-04x). On 2026-10-19, the documented commands updated Claude Code from 0.4.0 to 0.5.0 and installed 0.5.0 in Codex. `claude plugin list` reported 0.5.0. Both caches were compared with `git archive v0.5.0 plugin`. Codex matched exactly. Claude matched except for its runtime `.in_use` marker. Later that day, after the 0.5.1 tag was published, the chief observed both hosts update from 0.5.0 to 0.5.1. `claude plugin list` reported 0.5.1, and the Codex cache matched `git archive v0.5.1 plugin`. If your host retains an older copy, use its supported reinstall controls and preserve the complete resource layout. Confirm native discovery before invoking `$hugues-mode` or `/hstack:hugues-mode`.

Before using `watch-pr` or `orch` from a newly installed copy, prepare its Bun dependencies once. Use a session authorized to install packages and write that copy's scripts directory. Expand `<plugin>` to the absolute root of the copy actually loaded:

```sh
cd "<plugin>/skills/hugues-mode/scripts" && bun install --frozen-lockfile && bun "<plugin>/skills/hugues-mode/scripts/watch-pr/watch-pr" --help
```

Standard roots are `~/.claude/plugins/cache/hstack/hstack/0.5.1` and `~/.codex/plugins/cache/hstack/hstack/0.5.1`. A custom loaded root takes precedence. Require exit 0 and inspect `node_modules/commander/package.json` and `node_modules/.poteto-mode-tools-install-key`. The key must equal SHA-256 of `package.json`, a NUL byte and `bun.lock`, in that order. The help call lets the bootstrap write that key. A standalone frozen install does not write it. If setup lacks authority or the directory is not writable, hold the dependent step and report the expanded command. This setup does not widen the consumer sandbox.

For upgrades from 0.4.x, also follow [0.5.0's settings and plan migration](RELEASE-0.5.0.md#upgrade-from-04x). Preserve unrelated settings and evidence. Reconcile changed bindings explicitly. Do not rewrite hashes to hide unexpected drift.

## Validation

The release tree retains 502 collected top-level unittest cases, including the driver for 50 separate historical cases. The following checks run on the integrated 0.5.1 tree. They establish source and wiring contracts, separately from the native observations below.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 502 cases | Current source, installed adapter and helper contracts, plus the historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS | Plugin layout, manifests and installed payload checks. |
| `python3 scripts/check_core.py` | PASS | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

The final helper observations below used Xcode 27, build 27A266a, Swift 6.4, Gradle 8.13 and JDK 21. Each row is one observed native run through the final helper from [#107](https://github.com/hugues-vnsgn/hstack/pull/107). Counts are executed, failed and skipped. A failed native check is an observed helper result, not a passing test run.

| Native helper run | Observed result | Counts | Scope and limit |
|---|---|---|---|
| Xcode expected failure plus UI pass | Passed, complete | 2 / 0 / 0 | Owned iOS 27 simulator and retained xcresult. Expected failure counts as executed. No host workflow claim. |
| Xcode expected failure, intentional failure and pass | Failed, complete | 3 / 1 / 0 | Native failing test identity and diagnostics retained. |
| Mixed XCTest and Swift Testing | Passed, complete | 2 / 0 / 2 | Both runners executed in a host package. No iOS proof. |
| All-skipped XCTest | Incomplete, `zero_tests` | 0 / 0 / 1 | Cannot satisfy a requested test check. Verbose terminal evidence supplies skip visibility. |
| Swift Testing only | Passed, complete | 1 / 0 / 1 | Primary XML path, with a disabled case. Host package only. |
| One Swift Testing test with two issues | Failed, complete | 1 / 1 / 0 | Multiple issues count as one failed test. |
| Swift build with forwarded Clang argument | Passed, `build_only` | Unknown | Exact argument forwarding through a real build. No test execution claim. |
| Gradle ten failing JVM tests | Failed, complete | 10 / 10 / 0 | Native task and XML failure diagnostics. No Android runtime proof. |
| Gradle ten passing JVM tests | Passed, complete | 10 / 0 / 0 | Same native JVM test set after correction. |
| Gradle Kotlin compile error | Failed, `build_only` | Unknown | Native compiler diagnostics. Command exited normally with failure. |
| Gradle missing dependency offline | Failed, `build_only` | Unknown | Recorded dependency mutation produced the native cause. No offline-recovery workflow claim. |

All 11 bounded summaries are below 8,192 UTF-8 bytes. Their final helper SHA-256 is `c0db5c3db54abfa0f43359ab1cc5e97b0fcfb4c01facd0f3b1448d5a3111ef04`. Native drivers retained that source. Logs, summaries and native report copies were reopened after owned scratch and runtime cleanup. Four owned simulators were deleted and verified absent. No Android emulator was started.

Local retained evidence is under `hstack.worktrees/_notes/issue-105/worker-2-evidence/round-2/` beside the maintainer's repository. `native-final-receipt.json` binds the helper digest to the 11 summaries. `native-verified/` contains SwiftPM and Gradle requests, logs, reports and summaries. `xcode-verified/` contains the Xcode runs and inspector results. `native-verified/cleanup-and-reopened.json` and `xcode-verified/native-cleanup.json` record post-cleanup reads. These local artifacts are not bundled with the plugin. The committed [native capture index](../tests/fixtures/native-execution/captures.json) supports the source regressions.

Earlier Xcode attempts remain in `xcode-green/`. One timed out during diagnostic collection and remained incomplete. A later driver completed one case, then failed while inspecting the earlier incomplete bundle. The final two Xcode runs used `-collect-test-diagnostics never`. Earlier directories named `final` predate the last summary-budget correction and are not final-source proof. Earlier native KMP and Swift runs are historical helper evidence only.

Controlled public CLI regressions cover unavailable tools, interruption, timeout, wrong targets, stale or missing reports, metadata-only Xcode commands, aggregate XML limits, styled diagnostics and summary clipping. Native compiler errors on this machine were uncolored. ANSI diagnostic handling is established by controlled styled-error regressions. These cases are static/local contract evidence, not additional native runs.

An independent Claude Sonnet verifier reviewed the final helper at `473726b` and returned [PASS+NOTES](https://github.com/hugues-vnsgn/hstack/pull/107#issuecomment-6268399394). It ran real `swift build` and `swift test`, macOS `xcodebuild test` with `XCTExpectFailure` (3 executed, 1 failed), Gradle compile and offline failures, and controlled `gradlew` cases. The verdict does not cover fresh Claude Code or Codex mobile journeys.

No Swift/iOS, Kotlin/Android, KMP or CMP cell in the Claude Code and Codex workflow matrix is established by these helper observations. [#105](https://github.com/hugues-vnsgn/hstack/issues/105) remains open for those journeys.

## Known gaps

- The #105 host/domain matrix is unobserved on both hosts. This release claims no observed Swift/iOS, Kotlin/Android, KMP or CMP journey support. A macOS Swift package, one helper-driven iOS test or one KMP native task cannot replace that matrix. Fresh guidance selection, separate regression and production work, the justified impractical-test exception and current-build/install/runtime matching remain unobserved as complete consumer workflows.
- `claude-review` CI fails on every PR because of bot infrastructure. Both [#106's run](https://github.com/hugues-vnsgn/hstack/actions/runs/39234300925) and [#107's run](https://github.com/hugues-vnsgn/hstack/actions/runs/39232909550) fail with `is_error:true`. A passing maintenance check does not establish a completed Claude review. The watcher's match on bot login `claude` remains unconfirmed.
- Both final 0.5.0 host runs wrote their todo list after reproduction. Codex used a numbered list without Markdown checkboxes. No later observation in this release establishes full checklist adherence.
- The accepted 0.5.0 Claude run used headless bypassPermissions with hooks disabled. Interactive completion under normal permissions remains unobserved. Other configured plugins and task-management MCP tools were enabled, so the no-todo-tool fallback was not fully isolated.
- The final 0.5.0 host results each came from a single run. They do not establish repeatability.
- Codex's default read-only sandbox blocked first-time dependency installation into the plugin cache. The later pass established helper use after authorized setup. It did not establish installation under those permissions.
- The chief observed both hosts update from 0.5.0 to 0.5.1 on 2026-10-19 after the tag was published. `claude plugin list` reported 0.5.1, and the Codex cache matched `git archive v0.5.1 plugin`. A Claude Code process started before an update can keep loading its old cached copy. Restart Claude Code after updating.
- [#34](https://github.com/hugues-vnsgn/hstack/issues/34) items 4 through 6 remain deferred. They cover native history acquisition, managed cloud workers and loop or scheduler bindings. The optional Orca adapter in [#50](https://github.com/hugues-vnsgn/hstack/issues/50) and [#96](https://github.com/hugues-vnsgn/hstack/issues/96) also remain open.
- Native skill creation and categorized updates, whole-map maintenance, replacement-coordinator store recovery, Origin execution, Electron control and complete mobile consumer journeys were not established by the 0.5.0 release tests. This release adds no completed observation for those gaps.
- Native report compatibility is limited to the formats and toolchains actually exercised in the final helper evidence. Unsupported formats, ambiguous target identity and unavailable required tools remain explicit incomplete evidence. No broad toolchain compatibility or performance improvement is claimed.
- Gradle `-b` / `--build-file` and `-c` / `--settings-file` are not rejected by the helper. These options were removed in Gradle 9. Use the intended consumer build and settings files explicitly when selecting commands.
- Parameterized Swift Testing cases count once per function because native xunit records them that way. Failing xcodebuild diagnostics can include `RegisterExecutionPolicyException` noise.
- Native nonverbose XCTest output can omit skip visibility. Use the documented `--parallel --verbose` recipe. Ambiguous XML-only results remain incomplete. Hostile descendant-process cleanup remains unobserved.
- A standalone all-disabled Swift Testing run and a Swift build with multiple compiler errors are absent from the 11 final-source native observations. Captured and controlled regressions cover related parsing and diagnostics. Final Gradle observations exercise JVM tests, not a KMP native target. The earlier native KMP run remains historical evidence.
