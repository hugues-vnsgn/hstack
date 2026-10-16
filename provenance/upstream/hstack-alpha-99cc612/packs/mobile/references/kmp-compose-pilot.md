# Disposable KMP and Compose iOS pilot

`tests/kmp-compose-ios-pilot/` is a small full-Compose Android/iOS application
used to exercise the Gate F4 workflow. It is a fixture, not a production app.
Copy it before assigning an implementer or running a repair so the tracked
baseline remains reproducible.

## Baseline and contract

The shared `discountCents` function grants a ten-percent integer-cent discount
at 10,000 cents or more. The tracked fixture deliberately has `> 10_000`, so
the exact boundary is wrong. Its common baseline tests cover 9,999, 10,001, and
negative input; they intentionally do not cover the exact threshold. An
implementer adds the 10,000-cent regression, observes it fail, fixes the shared
function, and leaves the tracked fixture untouched.

The shared `CalculatorApp` has these tags:

| Element | Tag | Displayed text |
| --- | --- | --- |
| Subtotal input | `subtotal_input` | Entered cents |
| Calculate button | `calculate_button` | Calculate |
| Result text | `discount_result` | `Discount: N cents` |

The Android actual enables `testTagsAsResourceId` for the Compose root. The iOS
actual keeps the same tags as accessibility identifiers. Tapping **Calculate**
clears focus so an on-screen keyboard does not cover the result.

Android has application ID `com.hstack.gatef4.pilot` and entry activity
`com.hstack.gatef4.pilot.MainActivity`. The `:composeApp` module builds a static
`SharedUI.framework` for `iosArm64` and `iosSimulatorArm64`, with iOS 18.5 as
the host deployment target. Its deliberately small public Kotlin API is
`MainViewController()` in `MainViewController.kt`; the Objective-C bridge is
generated under `MainViewControllerKt` in `SharedUI.framework/Headers/SharedUI.h`.
Compose Multiplatform 1.11.1's static framework links an ICU object built for
iOS 18.5; setting the host below 18.5 produces a linker warning, so the host
and this documented floor stay aligned.

## Pinned profile

The version catalog pins Kotlin and its Compose compiler plugin to 2.4.10,
Compose Multiplatform to 1.11.1, AGP to 8.11.0, Gradle to 8.13, JDK to 21,
compile/target SDK to 36, and minimum SDK to 23. Compose dependencies use
direct `org.jetbrains.compose` Maven coordinates in the catalog rather than the
deprecated Gradle-plugin `compose.*` dependency aliases. The screen deliberately
uses only the cached runtime, foundation, foundation-layout, and UI artifacts;
it does not introduce an unrelated Material version pin.

## Build from a disposable copy

From the repository root, create an isolated copy:

```sh
PILOT_COPY=$(mktemp -d /tmp/gate-f4-kmp-compose.XXXXXX)
rsync -a --exclude build --exclude .gradle --exclude .kotlin --exclude local.properties \
  --exclude 'iosApp/**/xcuserdata' \
  packs/mobile/tests/kmp-compose-ios-pilot/ "$PILOT_COPY"/
cd "$PILOT_COPY"
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
export ANDROID_HOME="$HOME/Library/Android/sdk"
./gradlew :composeApp:testDebugUnitTest :composeApp:assembleDebug \
  :composeApp:linkDebugFrameworkIosSimulatorArm64 --offline --console=plain
```

The build outputs are:

- `composeApp/build/outputs/apk/debug/composeApp-debug.apk`
- `composeApp/build/test-results/testDebugUnitTest/`
- `composeApp/build/bin/iosSimulatorArm64/debugFramework/SharedUI.framework`

The fixture configures Kotlin's simulator test task to honor an explicit device
identifier when platform testing is separately allocated:

```sh
./gradlew :composeApp:iosSimulatorArm64Test \
  -PiosSimulatorId="$PILOT_SIMULATOR_ID" --console=plain
```

That property selects the existing simulator by UDID. It does not allocate or
boot a simulator; the coordinator owns that lifecycle. The Xcode host uses
direct integration and invokes `:composeApp:embedAndSignAppleFrameworkForXcode`
with the Xcode environment, which places the framework under
`composeApp/build/xcode-frameworks/`.

Build and test reports prove compilation and test execution only. Record
separate Android emulator and iOS simulator UI evidence for 9,999 → 0,
10,000 → 1,000, and 10,001 → 1,000 after the disposable repair is reviewed.

## Installed-app verification

Keep the original fixture faulty. After the worker repairs its disposable copy,
run the Android driver from the hstack repository with the built APK and an
explicit emulator serial:

```sh
python3 packs/mobile/tests/verify-kmp-compose-android.py \
  --serial "$PILOT_ANDROID_SERIAL" \
  --apk "$PILOT_COPY/composeApp/build/outputs/apk/debug/composeApp-debug.apk" \
  --evidence-dir "$PILOT_EVIDENCE/android-ui"
```

The evidence directory must be empty. The driver installs the APK, operates the
real controls, checks all three boundary cases, and retains screenshots, UI XML,
and the APK hash. A nonzero exit is expected for the planted baseline.

The Xcode `App` scheme includes `AppUITests`, which runs the same three cases and
retains screenshots. Target the allocated arm64 simulator explicitly; Intel
simulators are outside this fixture's profile. Keep the result bundle and test
log when invoking `xcodebuild test`. Xcode's project setting
`USER_SCRIPT_SANDBOXING=NO` permits the Gradle framework build phase; it does not
change the coding agent's permissions.

The iOS driver captures the build, test result bundle, screenshots, and app
executable hash in one empty evidence directory:

```sh
python3 packs/mobile/tests/verify-kmp-compose-ios.py \
  --simulator-id "$PILOT_SIMULATOR_ID" \
  --project-dir "$PILOT_COPY" \
  --evidence-dir "$PILOT_EVIDENCE/ios-ui"
```

Keep `JAVA_HOME` and `ANDROID_HOME` set as in the build commands. Passing requires
one executed XCTest method with no failures or skips, the requested simulator
ID, and all three named screenshots. The hash covers the app executable only;
it is not a hash of the entire app bundle. The driver does not allocate or stop
simulators.

## Reviewer handoff

Follow the [team recipe](../../../docs/gate-f-team.md) with a distinct reviewer
checkout. Put the reviewer's own absolute result destination and evidence root
in its brief, together with the canonical `review.json` example from that recipe.
Implementation output paths are not substitutes for reviewer paths. Validate
both the ordinary result schema and the review verdict before acceptance.

The first F4 run exposed this brief omission: the review passed its engineering
checks but wrote to another local folder and used an incompatible verdict shape.
Use a tracked follow-up to correct delivery and the schema without changing code
or weakening tests. Preserve the original artifacts when doing this recovery.
