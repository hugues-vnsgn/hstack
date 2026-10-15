# Issue 53: mobile tools under payload protection

The optional Claude macOS mobile recipe passed a bounded installed-consumer
regression on 15 October 2026. Both the coordinator and a fresh native worker
compiled a disposable KMP/CMP fixture and completed the selected tool checks
while the host rejected payload writes. This is not full autopilot qualification.

## Tested inputs

The runs used Claude Code 2.1.300 in `dontAsk` mode, Codex CLI 0.162.1
(shell engine only), macOS 27.0.1 arm64, Python 3.14.7, Bun 1.3.14,
Temurin JDK 21 and Gradle 8.13. The fixture was a disposable copy of
`kmp-compose-ios-pilot`; no live consumer source or persistent host settings changed.
Dependencies and the fixture's Android SDK path were prepared separately.

The tested worktree was based on `f68236a` with `source_dirty: true`. Its recorded
HEAD/plugin tree identifies the base, not the changed candidate. The exact Claude
binding was compared against every current authored adapter hash and the runner
hash before recording these results:

- Installed payload manifest SHA256: `fe008d20bbb8b0b77b57cc86015b10431c19a261b59f45772d17c17502eb1aab`.
- Native runner SHA256: `15cd5d58dfabf85658f6585e6d83f3b908a75c27f36d6689e24905449314e40b`.

The reviewed invocation selected JDK, Gradle, Kotlin/Native, Android-state,
Kotlin-daemon, Simulator-log and JVM-temporary paths plus `api.github.com`.
It enabled local binding, the recipe's CoreSimulator services and weaker network
isolation while retaining the exact payload denial and strict filesystem sandbox.
It supplied no unsandboxed command exception. Hooks and MCP were absent from this
fixture; their removal is not a consumer verification workaround.

## Failures that shaped the recipe

- The base recipe reproduced sandboxed `java_home` failing to discover the JDK.
- The first compilation attempt had a cold Gradle distribution cache. It failed;
  its logs were retained and dependencies were prepared outside the protected run.
- A prepared attempt reached Kotlin/Native but could not write its report to the
  JVM's actual temporary directory. That directory was then selected explicitly.
- An intermediate successful build used Kotlin's fallback after a denied daemon
  marker write. Selecting its existing daemon-state directory removed that failure.
- Allowing only the main CoreSimulator service and `simdiskimaged` let listings
  exit zero while reporting unavailable devices. A separate native diagnostic
  with launch-host and trampoline access reported available devices and spawned
  a read-only command inside the selected booted Simulator. The final recipe
  includes those services; the final combined run repeated the check.

## Observed combined result

In `mobile-qualified`, both actors ran exactly:

```sh
./gradlew --offline --no-daemon --rerun-tasks :composeApp:compileDebugKotlinAndroid :composeApp:compileKotlinIosSimulatorArm64
```

Each build exited zero with 19 actionable tasks executed and no Kotlin compiler
fallback. Gradle still reported an unavailable FSEvents stream, and the Android
SDK tooling reported an XML-version warning; neither stopped these compilations.

Both actors also completed the selected gates:

- `simctl list devices booted --json`: both existing devices were available.
- `simctl spawn <selected-udid> launchctl getenv HOME`: exited zero on the booted
  iOS 26.5 Simulator. This is process/service access, not an app interaction test.
- `adb devices -l`: exited zero. No Android device journey is claimed.
- `gh api repos/hugues-vnsgn/huguesStack --jq .full_name`: exited zero and returned
  the repository name. No forge mutation or publishing was attempted.

Before binding, the disposable payload accepted an append and creation and was
restored. Under protection, each actor's unchanged Python probe ran prepared
`helper-ready` and `watch-pr --help`, then received `PermissionError` for append,
create, rename, delete, chmod, alias and atomic replacement. Paired native file-tool
results recorded coordinator Write/Edit, alias and worker denials. Payload reads,
consumer/evidence writes, a consumer-local corrective artifact and a generated
verification artifact succeeded. The generated skill was not invoked.

Payload bytes, modes and inventory remained unchanged. The binding, settings,
probe and selected gate manifest remained unchanged. The copied mobile source
also stayed equal, excluding generated `.gradle`, `.kotlin` and `build` trees.

The separate `codex-final` run repeated the unlocked-copy control, prepared helper,
seven shell denials and read/write controls against the final inputs through the
Codex sandbox engine. It did not run Codex native file tools or a worker.

## Receipts and limits

Raw logs remain private under `~/huguesstack-evidence/2026-10-15-issue53/`.
The manifests were rehashed and verified:

| Directory | SHA256 of `SHA256.json` |
|---|---|
| `mobile-qualified` | `4f5867286a90a15eb111476b0d0c7c315e70169a4ad04640885cdad9e9ea9896` |
| `codex-final` | `4508a8219f36fd85ae8e52ae294ff5fb92c627bfd5a30cc723aa1a8bfda200c3` |

The [native regression guide](../tests/payload-boundary.md) describes reproduction.
The three additional Python cases bring the repository suite to 442; the full
suite passed. Static checks establish source/workflow wiring, not host behavior.

Auto-mode classifier acceptance, interactive effective-settings inspection,
Desktop, Intel Macs, other operating systems, full autopilot lifecycle, stack
publication, device UI tests and generic MCP/hook/service isolation remain gaps.
Localhost access and CoreSimulator access do not prove that existing services
inherit the shell's payload boundary. Required uncovered writers continue to hold
their dependent work. These receipts do not mark a different live bound root ready.
