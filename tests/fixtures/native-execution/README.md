# Captured native execution output

These files are original native output captured on 2026-10-19 with Swift 6.4,
Xcode 27.0 and the consumer Gradle wrappers. `captures.json` records exact
commands, working directories, exit codes and file hashes. The XML, JSON and
terminal bytes are inputs to installed public CLI regressions in
`tests/test_native_exec.py`. The helper implementation does not generate their
expected statuses or counts.

XCTest captures compare ordinary parallel output with `--verbose` output for
a real `XCTSkip` and a real passing XCTest. Only verbose output exposes terminal
case results on this toolchain. Swift Testing captures cover both enabled
runners, `--disable-xctest` primary-path output and `.disabled` count semantics.
The Xcode bundle contains one pass, one expected failure and one unexpected
failure. Its summary was captured with schema `0.4.0`.

Gradle captures include ten failing JVM tests, a Kotlin compiler error and an
offline missing-dependency failure from a disposable copy of the KMP fixture.
The missing dependency is intentional. The unmodified fixture resolved cached
dependencies successfully and is not represented as an offline failure here.
Swift compiler captures contain five source errors. The PTY variant includes
ANSI progress controls; diagnostic text itself was uncolored on this toolchain.

Text captures use binary diffs to preserve terminal bytes and trailing spaces.
Their full contents remain readable on disk. Absolute paths, timestamps and
simulator identity belong to the captured attempts. Replaying these files
through a controlled child tests helper interpretation, not native host adoption.
The original bundles, logs, source consumers, runnable capture scripts and
post-cleanup reads remain in the task evidence store.

## Issue 109 matrix regressions

The `u3-*.txt` files are matching diagnostic-line excerpts from the retained
issue 105 U3 evidence. They preserve original spelling and order. The iOS RED
excerpt includes the decisive assertion from original stdout line 357.

- `u3-ios-red.txt` comes from `ios-swiftui-codex/evidence/native/attempt-kvgary0w/stdout.log`.
- `u3-swiftpm-noise.txt` comes from `../u3-fixture-evidence/attempts/attempt-pylzix3u/stderr.log`, a retained passing SwiftPM fixture-preparation run with the same policy registration noise reported in finding 18. The U3 Claude cell retained no such raw line, so this adjacent passing capture supplies it.
- `u3-xcode-noise.txt` comes from `kmp-shared-codex/evidence/native/attempt-u2bc2tyi/stdout.log` and `stderr.log`.
- `u3-gradle-noise.txt` comes from `android-compose-codex/evidence/green-build/attempt-wlxierxb/stdout.log`.
- `adb-pass.txt` and `adb-failure.txt` are complete captured raw protocol output from `android-compose-codex/evidence/green-instrumentation.log` and `red-instrumentation.log`. The failing capture has a terminal failure without a start bundle. It still proves failure, while the parser marks its protocol incomplete.

The source root is the owner's local `hstack.worktrees/_notes/issue-105/u3-evidence/`.
`adb-zero.txt` and `adb-crash.txt` were captured on the worker-owned read-only Medium_Phone_API_36.1 during issue 109 proof. The zero run excluded the fixture class with `-e notClass`. The crash run force-stopped only the disposable fixture process during instrumentation. Both retained ADB process exit 0. Duplicate, conflicting and truncated variants are explicitly constructed parser counterexamples.
