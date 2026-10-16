# F4 KMP and Compose pilot verification

SHIP for the scoped F4 pilot. Both Work Units are accepted, owned resources are
stopped, and all acceptance-matrix rows pass.

The disposable pilot demonstrates a shared engineering repair through the Codex
team workflow. A fresh Terra worker added the 10,000-cent regression, observed
it fail on Android and iOS, changed `>` to `>=`, and passed all four shared
tests on each target. The supervisor then installed the staged APK and built
and tested the SwiftUI-hosted Compose app on the allocated iOS simulator.

## Runtime evidence

| Subtotal | Expected discount | Android | iOS |
| --- | --- | --- | --- |
| 9,999 | 0 | PASS | PASS |
| 10,000 | 1,000 | PASS | PASS |
| 10,001 | 1,000 | PASS | PASS |

The same exact-boundary UI check failed before the repair on both platforms;
see [baseline proof](baseline.md). No UI assertion was weakened. The iOS run
executed one XCTest method containing all three cases, with zero failures and
zero skips. The recorded simulator ID matches the allocated device. Source
hashes matched before and after UI verification.

Boundary screenshots: [Android](android-threshold.png), [iOS](ios-threshold.png).

The fixed APK hash is
`6470e6057157b4fa0899d090b4c340bdff92c42ba16e2e1e23a7402289f48da6`.
The iOS app executable hash is
`792862a434732bc665597fb1ede492001b29bb56df6f431d8d07809aef1f925d`;
this hash excludes the rest of the app bundle.

## Reviewed work

The implementation and reviewer have separate Work Units and Orca checkouts,
starting at disposable baseline `ccbbae970ac93b818e269215e883050c940fab87`.
A one-worker store budget serializes execution. Review was bound before the
implementation attempt. The raw worker result is retained separately from the
coordinator-combined result, which adds supervisor-owned UI checks.

Snapshot:
`319e16ad62feb4cba31e16eb79272189ff84e6c715fe09a3ba631e2f966e8ece`.
The supervisor compared all 115 captured evidence files and both changed source
files with their actual bytes, and verified the snapshot file hash. The snapshot
includes test logs/XMLs, APK, app executable, verifier sources, command evidence,
and screenshots. Full Xcode derived data and the raw result bundle remain in
local evidence; intermediate build files are not snapshot artifacts.

The independent reviewer reran both target test suites and both artifact builds,
verified all captured bytes, and returned the canonical passing verdict. The
implementation is accepted at revision 17 and the reviewer at revision 22;
both attempts are closed. The supervisor verified all 117 implementation and
12 reviewer accepted-artifact hashes.

The first reviewer brief omitted its role-specific result destination and
canonical verdict shape. Two tracked follow-ups corrected delivery/schema and
split the four command records into real argv arrays. Original outputs were
preserved; no code or test assertion changed during recovery. The disposable
coordinator template and mobile guide were corrected to prevent this omission.

## Local validation

`bash tests/run-gates.sh` passed: 152 core CLI tests, package validation, two
parser tests, and router self-tests. Shellcheck and Ruff passed in that
gate. Both new verification drivers passed Ruff and syntax checks. The Android
driver ran against the installed fixed APK; the iOS driver parsed both the
failing baseline result and the passing fixed run.

Separate Standards and Spec reviews passed after the command-evidence fixes;
see [review report](review.md). Final documentation reconciliation passed
both review axes before publication.

## Scope and retained evidence

This is a local debug-artifact pilot for KMP, Compose Multiplatform, Android,
and a thin SwiftUI iOS host. It does not certify production apps, native Swift
business logic, release signing, physical devices, Intel simulators, every
mobile toolchain, or deferred Gate E/provider integrations. AGP 8.11 emits
non-fatal Kotlin 2.4.10 metadata warnings. The host minimum is iOS 18.5, matching
the linked ICU object; runtime testing used iOS 26.4.1 on Apple Silicon.
Native task approvals remained supervised through Orca, as in the accepted
Gate D scope. No other provider or quota reset was used.

Raw evidence root:
`/var/folders/yd/86fjng8s4hbfhcz7_0yqcl9w0000gn/T/hstack-gate-f4-krthktsg`.
The `f4-live/implementation/` directory holds UI proof and the combined result;
`store/` holds Work Units and the captured snapshot. `local-gates.log` holds
local validation output. Disposable checkouts and source fixtures are retained;
the tracked fixture deliberately keeps its planted bug.

Cleanup is verified: both worker terminal inventories are empty; configured
capacity is 0/1 with an empty queue; pilot apps are uninstalled; the Android
emulator exited with code 0; the owned iOS simulator is shut down; and the Orca
streaming helper is stopped. The AVD, dedicated simulator, and disposable
checkouts are retained. See [compact evidence](final-evidence.json).
