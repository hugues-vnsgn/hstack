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
