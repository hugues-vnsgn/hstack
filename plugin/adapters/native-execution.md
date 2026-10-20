# Native build and test execution

## When the helper is required

Every build or test command using `xcodebuild`, `swift build` / `swift test`,
or Gradle in an Android/KMP/CMP project must go through the helper.
This rule depends on the command, not on the task being mobile.
Allow an exception for one command at a time, only when:

1. The helper does not support that command.
2. The helper returns a prerequisite error that the agent cannot resolve.

Run the excepted command and retain its raw logs in the task evidence store.
List each excepted command and its reason under Gaps in the final message.
An unsupported test step never excuses a build step or any other supported step.
The existing impractical-test exception is unchanged.

Before running Xcode, SwiftPM or consumer Gradle builds/tests, resolve the
consumer recipe, toolchain, project, scheme, destination, variant, module,
source set and supported test selector. An unresolved identity is a named
prerequisite. Consumer authority and native tool restrictions still apply.

## Run one selected check

The Python standard-library helper has three entrypoints:

```sh
python3 "<plugin>/adapters/native_exec.py" xcodebuild --request /task/xcode.json --store /task/evidence
python3 "<plugin>/adapters/native_exec.py" swiftpm --request /task/package.json --store /task/evidence
python3 "<plugin>/adapters/native_exec.py" gradle --request /task/gradle.json --store /task/evidence
```

Resolve `<plugin>` from the loaded mode path through [workflow tools](host-workflow-tools.md).
Use the established absolute task evidence store outside consumer and plugin.
The request is execution context, not a replacement native-report format:

```json
{
  "argv": ["swift", "test", "--parallel", "--verbose", "--filter", "ParserTests", "--xunit-output", "/task/results/package.xml"],
  "cwd": "/work/My Package",
  "operation": "test",
  "target": {"package": "/work/My Package"},
  "reports": ["/task/results/package.xml"],
  "env": {},
  "timeout_seconds": 900
}
```

The helper passes exact argv tokens without a shell. It applies explicit `env`
overrides and inherits other environment values without recording them. Keep
secrets out of requests and disclose required redactions as evidence limitations.
It never chooses commands, inserts flags, installs tools, retries or uploads.
Use `operation` `build` and empty `reports` for build-only checks. The default
timeout is 900 seconds; allowed values are greater than zero and at most 86,400.

| Tool | Identity and native report contract |
|---|---|
| `xcodebuild` | One `-project` or `-workspace`, explicit `-scheme` and `-destination`. Set `target.scheme` and `target.destination` to the exact argv values. Tests need `id=<device>` in the destination and `-resultBundlePath` equal to the single report path. Keep `-only-testing` selections in argv. Metadata, dependency-resolution, enumeration and dry-run modes cannot satisfy a build or test check. |
| `swiftpm` | `target.package` must match `--package-path` or `cwd`. XCTest needs `--parallel` to write xunit and `--verbose` to expose terminal case results for skip accounting on the observed Swift 6.4 toolchain. Tests need `--xunit-output` equal to the single report path. Keep configuration, triple, framework flags and filters in argv. Set `cwd` directly; `-C` and `--chdir` directory overrides are rejected. |
| `gradle` | Use the consumer root's `gradlew`. `target.task` is an explicit fully qualified argv task. `target.report_dir` and the single report path name that task's native output root, established from consumer configuration. Preserve variant, source set and supported filters. Set `cwd` directly; `-p` and `--project-dir` directory overrides are rejected. |

Resolve one target per attempt. Report roots must be absent, including SwiftPM's
`-swift-testing.xml` sibling. Choose unused native output paths or authorize
task-specific report cleanup in the consumer recipe. Existing reports are
retained as stale; the command is not launched. The helper deletes no consumer
files. Serialize commands sharing report outputs; another writer can invalidate
association. This helper cannot establish exclusivity over external writers.

## Read the bounded result

Stdout is one JSON object of at most **8,192 UTF-8 bytes including newline**.
It includes argv, cwd, target, command status, actual exit code, interpretation,
outcome, counts, decisive diagnostics and the absolute attempt directory.
Oversized argv, cwd or target fields explicitly say `omitted` and point to
`invocation.json`. Diagnostics retain up to six entries with first and last
errors, Kotlin compiler lines and Gradle's cause block. Styling is removed from
the summary. Each entry keeps at most 400 characters; long entries retain both
ends. `details_omitted` flags diagnostic, metadata and final byte-limit truncation.
Full detail remains in retained files.

Helper exit 0 means the requested check passed, 1 means an observed failure and
2 means incomplete evidence or an invalid prerequisite. Inspect the summary.
The native exit code is separate. `command_status` is `exited`, `signalled`,
`unavailable`, `denied`, `timed_out`, `interrupted` or `not_started`.
Interpretation is `build_only`, `complete`, `zero_tests`, `missing`, `unreadable`,
`unsupported`, `stale`, `target_mismatch`, `not_executed`, `incomplete` or `prerequisite`.
`outcome` is `passed`, `failed` or `incomplete`. Unknown counts are JSON `null`.
Executed counts exclude skips. A test passes only with normal command exit 0,
complete evidence, positive executed count and zero failures. Build-only success
has unknown test counts. Interrupted builds have incomplete interpretation.
Zero selected or all skipped tests never pass.

The summary's `target_verification` distinguishes `native_device`,
`invocation_and_fresh_reports` and `unverified` association.

Xcode retains original `.xcresult` and queries the selected toolchain's modern
`xcresulttool get test-results summary --schema-version 0.4.0`. The observed
Xcode 27 schema requires `expectedFailures`. Those tests count as executed,
while `failedTests` counts unexpected failures. Counts must be consistent and
reported device IDs and `Test - <scheme>` title must match. Failure diagnostics
include the test name. Inspection uses the request's `timeout_seconds`, with the
same 900-second default. Inspection argv, exit and raw output are saved separately,
including partial output after timeout.
Unavailable inspection and unknown schemas remain unsupported.

SwiftPM retains XCTest XML and Swift Testing's sibling independently when both
runners are enabled. With `--disable-xctest`, Swift Testing writes the primary
path. A missing enabled runner needs its own observed native zero-test summary
or remains incomplete. Explicit framework-disable flags limit the requested
check. Parallel XCTest XML can omit skip information. The helper reconciles
terminal case results by identity instead of adding repeated suite totals.
Missing or contradictory skip evidence leaves executed and skipped counts unknown.
Swift Testing's declared test count excludes disabled cases; Gradle's includes
skips. Swift Testing declares failure issues, so several failed expectations
can belong to one failed testcase. The summary counts failed tests and retains
each issue's diagnostic. XML counts leaf testcases without adding suite totals twice.
Inconsistent counts, duplicate identities and retry elements remain incomplete.
An XML report set over 32 MiB in aggregate is retained but unsupported for
interpretation.

Gradle needs per-testcase XML and the matching `> Task :module:task` execution
record. Select the supported plain console option when needed. Cached,
up-to-date, skipped and no-source task results cannot establish fresh execution.
Unknown native formats remain unsupported. JVM filtering does not imply that
instrumentation or Kotlin/Native tasks support the same filter.

XML commonly lacks platform/device identity. The discovered task/report mapping
and fresh command associate these reports; they do not prove an emulator or
iOS runtime. Optional `target.suite_pattern` matches `classname.name`; an
unexpected case is a target mismatch. Neither a matching suite nor a SwiftPM
host run establishes mobile proof.

## Retain each attempt

Every invocation gets a new directory containing `invocation.json`, raw
`stdout.log`, raw `stderr.log`, `reports.json`, native copies under `reports/`
and `summary.json`. The invocation records exact argv, cwd, target, source report
paths, explicit environment overrides, timeout and timestamps. The report
manifest records original paths, retained paths and file hashes. Every retry
keeps its own logs and failures. There is no shared latest-result file.

Handled interrupts/timeouts terminate the owned process group and retain partial
output. An uncatchable kill can leave no final summary; that is incomplete.
After authorized device and scratch cleanup, reopen the logs, summary and native
copies. A missing or unreadable artifact is an evidence gap. The helper cleans
up no runtime instances and removes no attempts.

During iteration run the narrowest relevant supported check. Preserve independently
observed RED/GREEN and separate mobile regression/production workers. The existing
impractical-test exception needs its concrete reason and executable runtime
reproduction, without an automated RED/GREEN claim. Focused helper checks do not
replace final integration, native caller or UI proof in the consumer recipe.

Native interfaces are documented by [SwiftPM](https://github.com/swiftlang/swift-package-manager/blob/main/Sources/PackageManagerDocs/Documentation.docc/SwiftTest.md),
[Gradle](https://docs.gradle.org/current/userguide/java_testing.html) and
[Xcode](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results).
Verify version-sensitive flags against the consumer's installed tool help.
